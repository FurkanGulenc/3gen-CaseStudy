from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.db.models import Project
from app.db.crud_user import get_current_user
import httpx
import xml.etree.ElementTree as ET

router = APIRouter()

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),  # 🔑 auth zorunlu
):
    # 1. DB’den proje bul
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Kullanıcıya ait mi kontrol et
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # 3. XML feed indir
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(project.feed_url)
            response.raise_for_status()
            xml_content = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feed fetch error: {str(e)}")

    # 4. Namespace
    ns = {"atom": "http://www.w3.org/2005/Atom", "g": "http://base.google.com/ns/1.0"}

    # 5. XML parse
    products = []
    try:
        root = ET.fromstring(xml_content)
        for entry in root.findall("atom:entry", ns):
            prod_id = entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else None
            image_url = entry.find("atom:image_link", ns).text if entry.find("atom:image_link", ns) is not None else None
            products.append({
                "id": prod_id,
                "image": image_url
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feed parse error: {str(e)}")

    # 6. Response
    return {
        "id": project.id,
        "name": project.name,
        "frame_image": project.frame_image,
        "pos_x": project.pos_x,
        "pos_y": project.pos_y,
        "width": project.width,
        "height": project.height,
        "radius": project.radius,
        "products": products
    }

