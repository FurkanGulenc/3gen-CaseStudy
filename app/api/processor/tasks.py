import os
import requests
import xml.etree.ElementTree as ET
import logging
import httpx
from celery import Celery
from PIL import Image, ImageDraw
from io import BytesIO
from datetime import datetime
from app.db.models import Project, OutputImage
from app.db.db_sync import SessionLocalSync

# ✅ Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("processor")

# ✅ Celery config
celery_app = Celery(
    "processor",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

ns = {"atom": "http://www.w3.org/2005/Atom", "g": "http://base.google.com/ns/1.0"}


def _rounded(im: Image.Image, radius: int) -> Image.Image:
    """Köşeleri yuvarlanmış görsel döndürür"""
    if not radius or radius <= 0:
        return im
    im = im.copy().convert("RGBA")
    w, h = im.size
    r = max(0, min(int(radius), min(w, h) // 2))
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    im.putalpha(mask)
    return im


@celery_app.task
def process_project_task(project_id: int, coords: dict = None):
    logger.info(f"[TASK START] Project {project_id}, coords={coords}")
    _process_project(project_id, coords)
    logger.info(f"[TASK END] Project {project_id}")


def _process_project(project_id: int, coords: dict = None):
    db = SessionLocalSync()
    try:
        logger.info(f"[DB] Looking for project {project_id}")
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"[ERROR] Project {project_id} not found.")
            return

        logger.info(
            f"[DB] Found project: id={project.id}, name={project.name}, feed_url={project.feed_url}"
        )

        # Koordinatları seç
        if coords:
            new_w = int(coords.get("width", project.width))
            new_h = int(coords.get("height", project.height))
            pos_x = int(coords.get("pos_x", project.pos_x))
            pos_y = int(coords.get("pos_y", project.pos_y))
            radius = int(coords.get("radius", project.radius or 0))
        else:
            new_w = int(project.width)
            new_h = int(project.height)
            pos_x = int(project.pos_x)
            pos_y = int(project.pos_y)
            radius = int(getattr(project, "radius", 0) or 0)

        logger.info(f"[FRAME COORDS] x={pos_x}, y={pos_y}, w={new_w}, h={new_h}, r={radius}")

        # Feed indir
        try:
            logger.info(f"[FEED] Downloading feed: {project.feed_url}")
            response = requests.get(project.feed_url, timeout=10)
            response.raise_for_status()
            xml_content = response.text
            logger.info(f"[FEED] Downloaded {len(xml_content)} chars")
        except Exception as e:
            logger.error(f"[ERROR] Feed fetch error: {e}")
            return

        # XML parse
        try:
            root = ET.fromstring(xml_content)
            entries = root.findall("atom:entry", ns)
            logger.info(f"[FEED] Parsed XML, found {len(entries)} entries")
        except Exception as e:
            logger.error(f"[ERROR] Feed parse error: {e}")
            return

        # output klasörü
        output_dir = f"media/outputs/{project_id}"
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"[FS] Output dir ready: {output_dir}")

        try:
            frame = Image.open(project.frame_image).convert("RGBA")
            logger.info(f"[FRAME] Loaded frame {project.frame_image} size={frame.width}x{frame.height}")
        except Exception as e:
            logger.error(f"[ERROR] Frame open failed: {e}")
            return

        success, failed = 0, 0

        for idx, entry in enumerate(entries, start=1):
            try:
                product_id = entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else None
                image_url = entry.find("atom:image_link", ns).text if entry.find("atom:image_link", ns) is not None else None

                logger.info(f"[ITEM {idx}] Start product_id={product_id}, url={image_url}")

                if not image_url:
                    logger.warning(f"[ITEM {idx}] No image url, skipping")
                    failed += 1
                    continue

                # indir
                r = httpx.get(image_url)
                r.raise_for_status()
                logger.info(f"[ITEM {idx}] Downloaded {len(r.content)} bytes")

                prod = Image.open(BytesIO(r.content)).convert("RGBA")
                logger.info(f"[ITEM {idx}] Opened product image size={prod.width}x{prod.height}")

                # resize
                prod_resized = prod.resize((new_w, new_h), Image.LANCZOS)

                # köşeleri yuvarla
                prod_resized = _rounded(prod_resized, radius)

                # clamp
                max_x = max(0, frame.width - new_w)
                max_y = max(0, frame.height - new_h)
                pos_x = max(0, min(pos_x, max_x))
                pos_y = max(0, min(pos_y, max_y))

                # birleştir
                composed = frame.copy().convert("RGBA")
                composed.alpha_composite(prod_resized, dest=(pos_x, pos_y))
                logger.info(f"[ITEM {idx}] Composited at {(pos_x, pos_y)}")

                # kaydet
                ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
                fname = f"{product_id or 'item'}_{ts}.png"
                out_path = os.path.join(output_dir, fname)
                composed.save(out_path)
                logger.info(f"[ITEM {idx}] Saved {out_path}")

                # DB kaydet
                oi = OutputImage(
                    project_id=project_id,
                    product_id=product_id,
                    source_image_url=image_url,
                    output_path=out_path,
                    status="PENDING",
                    rendered_at=datetime.utcnow(),
                )
                db.add(oi)
                db.commit()
                logger.info(f"[ITEM {idx}] DB commit ok")

                success += 1
            except Exception as e:
                failed += 1
                db.rollback()
                logger.error(f"[ITEM {idx}] ERROR: {e}")

        logger.info(f"[SUMMARY] total={len(entries)}, success={success}, failed={failed}")

    finally:
        db.close()
