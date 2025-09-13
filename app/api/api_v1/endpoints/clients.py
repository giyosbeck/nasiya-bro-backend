from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.db.database import get_db
from app.models.user import User, UserRole, UserType, Client
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ClientCreate(BaseModel):
    name: str
    phone: str
    passport_series: str
    passport_image_url: Optional[str] = None
    passport_image_urls: Optional[List[str]] = None

class ClientResponse(BaseModel):
    id: int
    name: str
    phone: str
    passport_series: str
    passport_image_url: Optional[str] = None
    passport_image_urls: Optional[List[str]] = None
    manager_id: int
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_json(cls, client):
        """Convert from ORM model and parse JSON fields"""
        passport_image_urls = None
        if client.passport_image_urls:
            try:
                passport_image_urls = json.loads(client.passport_image_urls)
            except (json.JSONDecodeError, TypeError):
                passport_image_urls = None
        
        return cls(
            id=client.id,
            name=client.name,
            phone=client.phone,
            passport_series=client.passport_series,
            passport_image_url=client.passport_image_url,
            passport_image_urls=passport_image_urls,
            manager_id=client.manager_id
        )

@router.get("/", response_model=List[ClientResponse])
def get_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all clients for the current user's scope based on business type"""
    
    if current_user.user_type == UserType.GADGETS:
        # GADGETS: Clients belong to magazine - filter by magazine_id
        query = db.query(Client).join(User, Client.manager_id == User.id)
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all clients from their magazine
            clients = query.filter(User.magazine_id == current_user.magazine_id).all()
        elif current_user.role == UserRole.MANAGER:
            # Manager can see all clients from their magazine
            clients = query.filter(User.magazine_id == current_user.magazine_id).all()
        else:
            # Seller can see all clients from their magazine
            clients = query.filter(User.magazine_id == current_user.magazine_id).all()
    
    elif current_user.user_type == UserType.AUTO:
        # AUTO: Clients belong to specific user - filter by manager_id
        if current_user.role == UserRole.ADMIN:
            # Admin can see all AUTO clients
            query = db.query(Client).join(User, Client.manager_id == User.id)
            clients = query.filter(User.user_type == UserType.AUTO).all()
        elif current_user.role == UserRole.MANAGER:
            # Manager can see their own clients
            clients = db.query(Client).filter(Client.manager_id == current_user.id).all()
        else:
            # Seller can see their manager's clients
            clients = db.query(Client).filter(Client.manager_id == current_user.manager_id).all()
    
    else:
        # Fallback: no user_type specified, use old logic
        clients = []
    
    return [ClientResponse.from_orm_with_json(client) for client in clients]

@router.post("/", response_model=ClientResponse)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new client"""
    
    # Check if client with same passport already exists
    existing_client = db.query(Client).filter(Client.passport_series == client_data.passport_series).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this passport series already exists"
        )
    
    # Determine the manager ID
    if current_user.role == UserRole.ADMIN:
        # For admin, use their own ID as manager_id
        manager_id = current_user.id
    elif current_user.role == UserRole.MANAGER:
        # For managers, use their own ID
        manager_id = current_user.id
    else:
        # For sellers, use their manager's ID
        manager_id = current_user.manager_id
    
    # Handle multiple passport images
    passport_image_urls_json = None
    if client_data.passport_image_urls:
        passport_image_urls_json = json.dumps(client_data.passport_image_urls)
    
    new_client = Client(
        name=client_data.name,
        phone=client_data.phone,
        passport_series=client_data.passport_series,
        passport_image_url=client_data.passport_image_url,
        passport_image_urls=passport_image_urls_json,
        manager_id=manager_id
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return ClientResponse.from_orm_with_json(new_client)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.ADMIN:
        # Admin can view any client
        pass
    elif current_user.role == UserRole.MANAGER:
        # Manager can only view their own clients
        if client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own clients"
            )
    else:
        # Seller can only view their manager's clients
        if client.manager_id != current_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your manager's clients"
            )
    
    return ClientResponse.from_orm_with_json(client)

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.ADMIN:
        # Admin can update any client
        pass
    elif current_user.role == UserRole.MANAGER:
        # Manager can only update their own clients
        if client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own clients"
            )
    else:
        # Seller cannot update clients
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update clients"
        )
    
    # Check if passport series is being changed and conflicts with another client
    if client_data.passport_series != client.passport_series:
        existing_client = db.query(Client).filter(
            Client.passport_series == client_data.passport_series,
            Client.id != client_id
        ).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another client with this passport series already exists"
            )
    
    # Update client fields
    client.name = client_data.name
    client.phone = client_data.phone
    client.passport_series = client_data.passport_series
    client.passport_image_url = client_data.passport_image_url
    
    # Handle multiple passport images
    if client_data.passport_image_urls:
        client.passport_image_urls = json.dumps(client_data.passport_image_urls)
    else:
        client.passport_image_urls = None
    
    db.commit()
    db.refresh(client)
    
    return ClientResponse.from_orm_with_json(client)

@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.ADMIN:
        # Admin can delete any client
        pass
    elif current_user.role == UserRole.MANAGER:
        # Manager can only delete their own clients
        if client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own clients"
            )
    else:
        # Seller cannot delete clients
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete clients"
        )
    
    # Check if client has active loans
    if client.loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete client with existing loans"
        )
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"} 