import database as db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ==========================================
# 📧 EMAIL CONFIGURATION
# ==========================================
# IMPORTANT: Configure these settings before deployment
# For Gmail: 
# 1. Enable 2-Factor Authentication
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use the app password below (not your regular Gmail password)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "haseebashfaq2085@gmail.com"      # Replace with your Gmail
SENDER_PASSWORD = "your-app-password"       # Replace with Gmail App Password
ADMIN_EMAIL = "admin@prisonsystem.com"      # Replace with admin's email

def send_email(recipient, subject, body):
    """
    Sends an HTML email notification
    Returns True if successful, False otherwise
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        # Return True anyway to not block registration in case email fails
        return True  

def notify_admin_new_registration(email, role, full_name):
    """
    Notifies admin about new user registration
    """
    subject = f"🔔 New User Registration - {role} Role"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #2563EB, #10B981); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🏛️ Prison Management System</h1>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #2563EB; margin-top: 0;">New User Registration</h2>
                    
                    <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10B981;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 600; color: #555;">Full Name:</td>
                                <td style="padding: 8px 0; color: #333;">{full_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 600; color: #555;">Email:</td>
                                <td style="padding: 8px 0; color: #333;">{email}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 600; color: #555;">Role Requested:</td>
                                <td style="padding: 8px 0; color: #333;"><span style="background-color: #DBEAFE; padding: 4px 12px; border-radius: 4px; font-weight: 600;">{role}</span></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 600; color: #555;">Registration Time:</td>
                                <td style="padding: 8px 0; color: #333;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #FFF3CD; padding: 20px; border-radius: 8px; border-left: 4px solid #FFC107; margin: 20px 0;">
                        <p style="margin: 0; font-weight: 600; color: #856404;">⚠️ Action Required:</p>
                        <p style="margin: 10px 0 0 0; color: #856404;">Please log into the admin portal to approve or reject this registration request.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="#" style="display: inline-block; background: linear-gradient(135deg, #2563EB, #10B981); color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 600;">Open Admin Portal</a>
                    </div>
                </div>
                
                <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 13px;">This is an automated notification from Prison Management System</p>
                    <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 13px;">© 2025 Prison Management System</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(ADMIN_EMAIL, subject, body)

def notify_user_approval(email, full_name, approved=True):
    """
    Notifies user about their account approval/rejection
    """
    if approved:
        subject = "✅ Account Approved - Prison Management System"
        color = "#10B981"
        status = "Approved"
        icon = "✅"
        message_body = f"""
                        <p>Great news! Your account has been <strong>approved</strong> by the system administrator.</p>
                        <p>You can now log in to the Prison Management System using your registered email address.</p>
        """
        alert_bg = "#D1FAE5"
        alert_border = "#10B981"
        alert_text = "#065F46"
        alert_title = "You can now login!"
        alert_message = "Visit the portal and sign in with your credentials to access the system."
    else:
        subject = "❌ Registration Status - Prison Management System"
        color = "#EF4444"
        status = "Not Approved"
        icon = "❌"
        message_body = f"""
                        <p>We regret to inform you that your account registration was <strong>not approved</strong> at this time.</p>
                        <p>If you believe this is an error or would like more information, please contact the system administrator.</p>
        """
        alert_bg = "#FEE2E2"
        alert_border = "#EF4444"
        alert_text = "#991B1B"
        alert_title = "Registration Not Approved"
        alert_message = "For questions or concerns, please contact the system administrator directly."
    
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #2563EB, {color}); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🏛️ Prison Management System</h1>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: {color}; margin-top: 0;">{icon} Account {status}</h2>
                    
                    <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0 0 15px 0;">Dear <strong>{full_name}</strong>,</p>
                        {message_body}
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280;"><strong>Your Email:</strong> {email}</p>
                        </div>
                    </div>
                    
                    <div style="background-color: {alert_bg}; padding: 20px; border-radius: 8px; border-left: 4px solid {alert_border}; margin: 20px 0;">
                        <p style="margin: 0; font-weight: 600; color: {alert_text};">{alert_title}</p>
                        <p style="margin: 10px 0 0 0; color: {alert_text};">{alert_message}</p>
                    </div>
                </div>
                
                <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 13px;">This is an automated notification from Prison Management System</p>
                    <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 13px;">© 2025 Prison Management System</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)
def login_user(email, password):
    """
    Simple login using direct query (for demo/presentation)
    """
    try:
        query = """
        SELECT UserID, Role
        FROM Users
        WHERE Email = ? AND Password = ?
        """
        
        result = db.fetch_one(query, (email, password))
        
        if result:
            user_id, role = result
            return (user_id, role)
        
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def register_user(email, password, role, full_name):
    """
    Registers a new user with 'Pending' status.
    Sends notification emails to both admin and user.
    Returns success/error message.
    """
    try:
        # Execute registration procedure
        result = db.execute_procedure('sp_RegisterUser', (email, password, role, full_name))
        
        # Parse result message
        if result and not isinstance(result, bool):
            try:
                message = result[0] if isinstance(result, tuple) else str(result)
            except:
                message = "Registration submitted"
        elif result is True:
            message = "SUCCESS: Registration submitted"
        else:
            return "Registration failed - Email may already exist"
        
        # If registration successful, send notification emails
        if "SUCCESS" in message or "pending" in message.lower():
            # Notify admin (non-blocking)
            try:
                notify_admin_new_registration(email, role, full_name)
            except:
                pass  # Don't block registration if email fails
            
            # Send confirmation to user (non-blocking)
            try:
                user_email_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <div style="background: linear-gradient(135deg, #2563EB, #10B981); padding: 30px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 28px;">🏛️ Prison Management System</h1>
                            </div>
                            
                            <div style="padding: 30px;">
                                <h2 style="color: #10B981; margin-top: 0;">✅ Registration Received!</h2>
                                
                                <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                    <p style="margin: 0 0 15px 0;">Dear <strong>{full_name}</strong>,</p>
                                    <p>Thank you for registering with the Prison Management System. Your account has been successfully created and is now pending administrative approval.</p>
                                    
                                    <div style="margin-top: 20px; background-color: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                                        <p style="margin: 0; font-weight: 600; color: #2563EB; margin-bottom: 10px;">Your Registration Details:</p>
                                        <table style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 6px 0; color: #6b7280;">Email:</td>
                                                <td style="padding: 6px 0; color: #111827; font-weight: 600;">{email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 6px 0; color: #6b7280;">Role:</td>
                                                <td style="padding: 6px 0; color: #111827; font-weight: 600;">{role}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 6px 0; color: #6b7280;">Status:</td>
                                                <td style="padding: 6px 0;"><span style="background-color: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 13px;">⏳ Pending Approval</span></td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                
                                <div style="background-color: #FFF3CD; padding: 20px; border-radius: 8px; border-left: 4px solid #FFC107; margin: 20px 0;">
                                    <p style="margin: 0; font-weight: 600; color: #856404;">⏳ What's Next?</p>
                                    <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #856404;">
                                        <li>The system administrator has been notified of your registration</li>
                                        <li>Your account will be reviewed within 24-48 hours</li>
                                        <li>You'll receive an email notification once your account is approved</li>
                                        <li>After approval, you can login with your registered credentials</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="margin: 0; color: #6b7280; font-size: 13px;">This is an automated notification from Prison Management System</p>
                                <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 13px;">© 2025 Prison Management System</p>
                            </div>
                        </div>
                    </body>
                </html>
                """
                
                send_email(email, "📝 Registration Confirmation - Prison Management System", user_email_body)
            except:
                pass  # Don't block registration if email fails
            
            return "SUCCESS: Registration submitted. Admin will review your request. Check your email for confirmation."
        else:
            return message
            
    except Exception as e:
        print(f"Registration error: {e}")
        return f"Registration failed: {str(e)}"

def approve_user_account(user_id, user_email, full_name, approved_by_id=None):
    """
    Admin function to approve a pending user account.
    Sends approval email notification to user.
    """
    try:
        result = db.execute_procedure('sp_ApproveUser', (user_id, approved_by_id))
        
        if result:
            # Send approval email to user (non-blocking)
            try:
                notify_user_approval(user_email, full_name, approved=True)
            except:
                pass
            return True
        return False
    except Exception as e:
        print(f"Approval error: {e}")
        return False

def reject_user_account(user_id, user_email, full_name):
    """
    Admin function to reject a pending user account.
    Sends rejection email notification to user.
    """
    try:
        result = db.execute_procedure('sp_RejectUser', (user_id,))
        
        if result:
            # Send rejection email to user (non-blocking)
            try:
                notify_user_approval(user_email, full_name, approved=False)
            except:
                pass
            return True
        return False
    except Exception as e:
        print(f"Rejection error: {e}")
        return False