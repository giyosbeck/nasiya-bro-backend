import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationStatus

class NotificationService:
    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def send_push_notification(
        self,
        push_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Send push notification via Expo Push API"""
        try:
            payload = {
                "to": push_token,
                "title": title,
                "body": body,
                "sound": "default",
                "priority": "high"
            }
            
            if data:
                payload["data"] = data
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.EXPO_PUSH_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            response_data = response.json()
            
            # Update notification status in database
            if notification_id and db:
                await self._update_notification_status(
                    notification_id, 
                    response, 
                    response_data,
                    db
                )
            
            # Check if notification was accepted
            if response.status_code == 200:
                if "data" in response_data and len(response_data["data"]) > 0:
                    result = response_data["data"][0]
                    if result.get("status") == "ok":
                        return True
                    else:
                        print(f"Expo push error: {result.get('message', 'Unknown error')}")
                        return False
                return True
            else:
                print(f"Push notification failed: {response.status_code} - {response_data}")
                return False
                
        except Exception as e:
            print(f"Error sending push notification: {str(e)}")
            
            # Update notification status to failed
            if notification_id and db:
                try:
                    notification = db.query(Notification).filter(
                        Notification.id == notification_id
                    ).first()
                    if notification:
                        notification.status = NotificationStatus.failed
                        notification.error_message = str(e)
                        db.commit()
                except Exception as db_error:
                    print(f"Failed to update notification status: {str(db_error)}")
            
            return False
    
    async def _update_notification_status(
        self,
        notification_id: int,
        response: httpx.Response,
        response_data: Dict[str, Any],
        db: Session
    ):
        """Update notification status based on Expo response"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if not notification:
                return
            
            if response.status_code == 200:
                if "data" in response_data and len(response_data["data"]) > 0:
                    result = response_data["data"][0]
                    if result.get("status") == "ok":
                        notification.status = NotificationStatus.sent
                        notification.sent_at = datetime.now()
                    else:
                        notification.status = NotificationStatus.failed
                        notification.error_message = result.get("message", "Unknown error")
                else:
                    notification.status = NotificationStatus.sent
                    notification.sent_at = datetime.now()
            else:
                notification.status = NotificationStatus.failed
                notification.error_message = f"HTTP {response.status_code}: {response_data}"
            
            db.commit()
            
        except Exception as e:
            print(f"Error updating notification status: {str(e)}")
    
    async def send_bulk_push_notifications(
        self,
        notifications: list,
        db: Optional[Session] = None
    ) -> Dict[str, int]:
        """Send multiple push notifications efficiently"""
        results = {
            "sent": 0,
            "failed": 0,
            "total": len(notifications)
        }
        
        # Prepare bulk payload for Expo
        messages = []
        notification_map = {}
        
        for i, notif in enumerate(notifications):
            message = {
                "to": notif["push_token"],
                "title": notif["title"],
                "body": notif["body"],
                "sound": "default",
                "priority": "high"
            }
            
            if notif.get("data"):
                message["data"] = notif["data"]
            
            messages.append(message)
            notification_map[i] = notif.get("notification_id")
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate", 
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.EXPO_PUSH_URL,
                json=messages,
                headers=headers,
                timeout=60.0
            )
            
            response_data = response.json()
            
            # Process results
            if response.status_code == 200 and "data" in response_data:
                for i, result in enumerate(response_data["data"]):
                    notification_id = notification_map.get(i)
                    
                    if result.get("status") == "ok":
                        results["sent"] += 1
                        # Update database status
                        if notification_id and db:
                            await self._mark_notification_sent(notification_id, db)
                    else:
                        results["failed"] += 1
                        # Update database with error
                        if notification_id and db:
                            await self._mark_notification_failed(
                                notification_id, 
                                result.get("message", "Unknown error"), 
                                db
                            )
            else:
                results["failed"] = results["total"]
                
        except Exception as e:
            print(f"Bulk notification error: {str(e)}")
            results["failed"] = results["total"]
        
        return results
    
    async def _mark_notification_sent(self, notification_id: int, db: Session):
        """Mark notification as sent"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if notification:
                notification.status = NotificationStatus.sent
                notification.sent_at = datetime.now()
                db.commit()
        except Exception as e:
            print(f"Error marking notification as sent: {str(e)}")
    
    async def _mark_notification_failed(self, notification_id: int, error_message: str, db: Session):
        """Mark notification as failed"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if notification:
                notification.status = NotificationStatus.failed
                notification.error_message = error_message
                db.commit()
        except Exception as e:
            print(f"Error marking notification as failed: {str(e)}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Singleton instance
notification_service = NotificationService()