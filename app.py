from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, Response
import os
import json
from functools import wraps
from record_keeper import RecordKeeper, AuthManager, DocumentRecord
from werkzeug.utils import secure_filename
import time
import threading
from datetime import datetime
import uuid
import queue
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_change_this_in_production')

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

keeper = RecordKeeper()
auth_manager = AuthManager()

# Real-time updates
connected_clients = set()
update_queue = queue.Queue()

# Helper function to broadcast updates to all clients
def broadcast_update(update_type, data):
    """Broadcast an update to all connected clients."""
    if connected_clients:  # Only queue updates if there are connected clients
        update = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        update_queue.put(update)

# System Settings Management
class SystemSettings:
    def __init__(self, settings_file='system_settings.json'):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load system settings from JSON file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings if file doesn't exist
        return {
            "system_name": "🏛️ LGU Record Keeping System",
            "logo_url": "",
            "theme": {
                "primary_color": "#1e3a8a",
                "secondary_color": "#3b82f6",
                "accent_color": "#fbbf24",
                "accent_light": "#fef3c7",
                "success_color": "#10b981",
                "danger_color": "#ef4444",
                "warning_color": "#f59e0b",
                "info_color": "#3b82f6",
                "background_color": "#f8fafc",
                "card_background": "#ffffff",
                "text_color": "#1e293b",
                "text_light": "#64748b",
                "border_color": "#e2e8f0",
                "header_background": "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)",
                "sidebar_background": "#f1f5f9",
                "font_family": "'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif",
                "font_size": "16px",
                "header_font_size": "2.25rem",
                "font_weight": "500",
                "shadow_sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                "shadow_md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
                "shadow_lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
                "border_radius": "0.75rem",
                "border_radius_sm": "0.375rem"
            },
            "branding": {
                "show_logo": True,
                "logo_position": "left",
                "system_description": "Document Management and Record Keeping System",
                "footer_text": "Powered by LGU Record Keeping System"
            }
        }
    
    def save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def update_setting(self, key_path, value):
        """Update a specific setting using dot notation (e.g., 'theme.primary_color')."""
        keys = key_path.split('.')
        current = self.settings
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
    
    def get_setting(self, key_path, default=None):
        """Get a specific setting using dot notation."""
        keys = key_path.split('.')
        current = self.settings
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

system_settings = SystemSettings()

# Context processor to make system settings available in all templates
@app.context_processor
def inject_system_settings():
    return {
        'system_settings': system_settings.settings,
        'get_setting': system_settings.get_setting
    }

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Access denied: Admin privileges required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if auth_manager.login(username, password):
            session['username'] = username
            session['role'] = auth_manager.get_current_user().role
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    auth_manager.logout()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    # Both users and admins see the tile dashboard upon login
    user_role = session.get('role', 'user')
    records = keeper.get_all_records()
    stats = keeper.get_statistics() if user_role == 'admin' else None
    return render_template('tile_dashboard.html', records=records, statistics=stats, user_role=user_role)

@app.route('/records')
@login_required
def records_page():
    # This shows records with appropriate functionality based on user role
    records = keeper.get_all_records()
    user_role = session.get('role', 'user')
    stats = keeper.get_statistics() if user_role == 'admin' else None
    return render_template('admin_dashboard.html', records=records, statistics=stats, user_role=user_role)

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Redirect to records page for admin functionality
    return redirect(url_for('records_page'))

@app.route('/add', methods=['POST'])
@login_required
def add_record():
    try:
        sender = request.form['sender']
        subject = request.form['subject']
        destination = request.form['destination']
        new_record = keeper.add_record(sender, subject, destination)
        
        # Broadcast the new record to all connected clients
        broadcast_update("record_added", new_record.to_dict())
        
        flash('Record added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding record: {e}', 'danger')
    
    # Redirect to records page to see changes immediately
    return redirect(url_for('records_page'))

@app.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    # Find the record
    record = None
    for r in keeper.get_all_records():
        if r.id == record_id:
            record = r
            break
    
    if not record:
        flash('Record not found.', 'warning')
        return redirect(url_for('records_page'))
    
    if request.method == 'POST':
        try:
            # Get form data
            sender = request.form.get('sender', '').strip()
            subject = request.form.get('subject', '').strip()
            destination = request.form.get('destination', '').strip()
            date = request.form.get('date', '').strip()
            status = request.form.get('status', '').strip()
            
            # Validate required fields
            if not sender or not subject:
                flash('Sender and Subject are required fields.', 'danger')
                return redirect(url_for('edit_record', record_id=record_id))
            
            # Validate status
            valid_statuses = ['Pending', 'Completed']
            if status and status not in valid_statuses:
                flash(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 'danger')
                return redirect(url_for('edit_record', record_id=record_id))
            
            # Update the record
            success = keeper.edit_record(
                record_id,
                sender=sender,
                subject=subject,
                destination=destination,
                date=date if date else record.date,
                status=status if status else record.status
            )
            
            if success:
                # Get the updated record for broadcasting
                updated_record = None
                for rec in keeper.get_all_records():
                    if rec.id == record_id:
                        updated_record = rec.to_dict()
                        break
                
                # Broadcast the update to all connected clients
                if updated_record:
                    broadcast_update("record_updated", updated_record)
                
                flash('Record updated successfully!', 'success')
                return redirect(url_for('records_page'))
            else:
                flash('Failed to update record.', 'danger')
                
        except Exception as e:
            flash(f'Error updating record: {e}', 'danger')
    
    return render_template('edit_record.html', record=record)

@app.route('/mark_done/<record_id>')
@login_required
def mark_record_done(record_id):
    if keeper.mark_as_done(record_id):
        # Get the updated record for broadcasting
        updated_record = None
        for rec in keeper.get_all_records():
            if rec.id == record_id:
                updated_record = rec.to_dict()
                break
        
        # Broadcast the status update to all connected clients
        if updated_record:
            broadcast_update("record_updated", updated_record)
        
        flash('Record marked as done successfully!', 'success')
    else:
        flash('Record not found.', 'warning')
    return redirect(url_for('records_page'))

@app.route('/delete/<record_id>')
@admin_required
def delete_record(record_id):
    if keeper.delete_record(record_id):
        # Broadcast the deletion to all connected clients
        broadcast_update("record_deleted", {"id": record_id})
        
        flash('Record deleted successfully!', 'success')
    else:
        flash('Record not found.', 'warning')
    return redirect(url_for('records_page'))

@app.route('/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    """Handle bulk operations on multiple records."""
    try:
        action = request.form.get('action')
        record_ids = request.form.getlist('record_ids')
        
        if not record_ids:
            flash('No records selected.', 'warning')
            return redirect(url_for('records_page'))
        
        success_count = 0
        total_count = len(record_ids)
        updated_records = []  # Track updated records for broadcasting
        
        if action == 'mark_completed':
            for record_id in record_ids:
                if keeper.mark_as_done(record_id):
                    success_count += 1
                    # Get the updated record for broadcasting
                    for rec in keeper.get_all_records():
                        if rec.id == record_id:
                            updated_records.append(rec.to_dict())
                            break
            flash(f'{success_count} of {total_count} records marked as completed.', 'success')
            
        elif action == 'mark_pending':
            for record_id in record_ids:
                success = keeper.edit_record(
                    record_id,
                    status='Pending'
                )
                if success:
                    success_count += 1
                    # Get the updated record for broadcasting
                    for rec in keeper.get_all_records():
                        if rec.id == record_id:
                            updated_records.append(rec.to_dict())
                            break
            flash(f'{success_count} of {total_count} records marked as pending.', 'success')
            
        elif action == 'delete' and session.get('role') == 'admin':
            deleted_ids = []
            for record_id in record_ids:
                if keeper.delete_record(record_id):
                    success_count += 1
                    deleted_ids.append(record_id)
            
            # Broadcast deletions
            for record_id in deleted_ids:
                broadcast_update("record_deleted", {"id": record_id})
            
            # Check if all records were deleted and add appropriate message
            remaining_records = keeper.get_all_records()
            if len(remaining_records) == 0 and success_count > 0:
                flash(f'{success_count} of {total_count} records deleted. Record numbering reset to start from 001 for next record.', 'success')
            else:
                flash(f'{success_count} of {total_count} records deleted.', 'success')
            
        else:
            flash('Invalid action or insufficient permissions.', 'danger')
        
        # Broadcast all record updates for mark completed/pending actions
        for updated_record in updated_records:
            broadcast_update("record_updated", updated_record)
        
        # If we have updates, also send a bulk update notification
        if updated_records:
            bulk_update_data = {
                "action": action,
                "count": success_count,
                "total": total_count,
                "updated_records": updated_records
            }
            broadcast_update("bulk_update", bulk_update_data)
            
    except Exception as e:
        flash(f'Error performing bulk action: {e}', 'danger')
    
    return redirect(url_for('records_page'))

@app.route('/export')
@app.route('/export/<format_type>')
@login_required
def export_records(format_type='excel'):
    try:
        records = keeper.get_all_records()
        if not records:
            flash('No records available to export.', 'warning')
            return redirect(url_for('home'))
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'excel':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], f'records_export_{timestamp}.xlsx')
            if keeper.export_to_excel(filename):
                # Send file as download
                return send_file(
                    filename,
                    as_attachment=True,
                    download_name=f'records_export_{timestamp}.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                flash('Failed to export Excel file.', 'danger')
                return redirect(url_for('home'))
                
        elif format_type == 'csv':
            import pandas as pd
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], f'records_export_{timestamp}.csv')
            df.to_csv(filename, index=False, encoding='utf-8')
            # Send file as download
            return send_file(
                filename,
                as_attachment=True,
                download_name=f'records_export_{timestamp}.csv',
                mimetype='text/csv'
            )
            
        elif format_type == 'json':
            import json
            data = [record.to_dict() for record in records]
            filename = os.path.join(app.config['UPLOAD_FOLDER'], f'records_export_{timestamp}.json')
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Send file as download
            return send_file(
                filename,
                as_attachment=True,
                download_name=f'records_export_{timestamp}.json',
                mimetype='application/json'
            )
            
    except Exception as e:
        flash(f'Error exporting records: {e}', 'danger')
        return redirect(url_for('home'))

@app.route('/search', methods=['GET'])
@login_required
def search_records():
    query = request.args.get('q', '').strip()
    
    if not query:
        # Return all records if no query
        records = keeper.get_all_records()
    else:
        # Search records
        records = keeper.search_records(query)
    
    # Convert records to dictionary format for JSON response
    records_data = []
    for record in records:
        records_data.append({
            'id': record.id,
            'date': record.date,
            'sender': record.sender,
            'subject': record.subject,
            'destination': record.destination,
            'status': record.status
        })
    
    return jsonify({
        'records': records_data,
        'count': len(records_data),
        'query': query
    })

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('home'))
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Get import mode from form (append or replace)
        import_mode = request.form.get('import_mode', 'append')
        replace_existing = (import_mode == 'replace')
        
        success = keeper.import_from_excel(filename, replace_existing)
        if success:
            if replace_existing:
                flash('Records replaced successfully!', 'success')
            else:
                flash('Records imported and added to existing data!', 'success')
        else:
            flash('Failed to import records.', 'danger')
    return redirect(url_for('home'))

@app.route('/export/backup')
@admin_required
def export_backup():
    try:
        records = keeper.get_all_records()
        if not records:
            flash('No records available to backup.', 'warning')
            return redirect(url_for('home'))
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create comprehensive backup with metadata
        backup_data = {
            'backup_info': {
                'created_at': datetime.now().isoformat(),
                'created_by': session.get('username', 'Unknown'),
                'total_records': len(records),
                'backup_version': '1.0'
            },
            'records': [record.to_dict() for record in records],
            'statistics': keeper.get_statistics()
        }
        
        # Export as JSON backup file
        import json
        filename = os.path.join(app.config['UPLOAD_FOLDER'], f'backup_{timestamp}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Send file as download
        return send_file(
            filename,
            as_attachment=True,
            download_name=f'backup_{timestamp}.json',
            mimetype='application/json'
        )
        
    except Exception as e:
        flash(f'Error creating backup: {e}', 'danger')
        return redirect(url_for('home'))

@app.route('/restore_backup', methods=['POST'])
@admin_required
def restore_backup():
    try:
        if 'backup_file' not in request.files:
            flash('No backup file selected.', 'danger')
            return redirect(url_for('home'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('No backup file selected.', 'danger')
            return redirect(url_for('home'))
        
        if not file.filename.endswith('.json'):
            flash('Invalid file type. Please upload a JSON backup file.', 'danger')
            return redirect(url_for('home'))
        
        # Save uploaded file temporarily
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filename)
        
        # Get restore mode from form (append or replace)
        restore_mode = request.form.get('restore_mode', 'replace')
        replace_existing = (restore_mode == 'replace')
        
        # Restore from backup
        success = keeper.restore_from_backup(filename, replace_existing)
        
        if success:
            # Broadcast update to all connected clients about the restore
            if replace_existing:
                broadcast_update("bulk_update", {
                    "action": "restore_replace",
                    "count": len(keeper.get_all_records()),
                    "total": len(keeper.get_all_records()),
                    "message": "System restored from backup (all records replaced)"
                })
                flash('Backup restored successfully! All existing records were replaced.', 'success')
            else:
                broadcast_update("bulk_update", {
                    "action": "restore_append",
                    "count": len(keeper.get_all_records()),
                    "total": len(keeper.get_all_records()),
                    "message": "Backup records added to existing data"
                })
                flash('Backup restored successfully! Records were added to existing data.', 'success')
        else:
            flash('Failed to restore backup. Please check the file format and try again.', 'danger')
        
        # Clean up temporary file
        try:
            os.remove(filename)
        except:
            pass
        
    except Exception as e:
        flash(f'Error restoring backup: {e}', 'danger')
    
    return redirect(url_for('home'))

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard with detailed insights."""
    try:
        records = keeper.get_all_records()
        statistics = keeper.get_statistics()
        user_role = session.get('role', 'user')
        
        # Calculate additional analytics
        from datetime import datetime, timedelta
        import calendar
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_records = []
        for r in records:
            if r.date and r.date != "No Date":
                try:
                    date_obj = datetime.strptime(r.date.split(' ')[0], '%Y-%m-%d')
                    if date_obj >= thirty_days_ago:
                        recent_records.append(r)
                except ValueError:
                    continue  # Skip records with invalid date format
        
        # Monthly breakdown
        monthly_data = {}
        for record in records:
            try:
                if record.date and record.date != "No Date":
                    date_obj = datetime.strptime(record.date.split(' ')[0], '%Y-%m-%d')
                    month_key = f"{date_obj.year}-{date_obj.month:02d}"
                    month_name = f"{calendar.month_name[date_obj.month]} {date_obj.year}"
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'name': month_name, 'count': 0, 'pending': 0, 'completed': 0}
                    monthly_data[month_key]['count'] += 1
                    if record.status == 'Pending':
                        monthly_data[month_key]['pending'] += 1
                    else:
                        monthly_data[month_key]['completed'] += 1
            except (ValueError, AttributeError):
                continue  # Skip records with invalid date format
        
        # Sort monthly data by date
        sorted_monthly = dict(sorted(monthly_data.items(), reverse=True))
        
        # Top senders and destinations
        sender_counts = {}
        destination_counts = {}
        for record in records:
            sender_counts[record.sender] = sender_counts.get(record.sender, 0) + 1
            if record.destination:
                destination_counts[record.destination] = destination_counts.get(record.destination, 0) + 1
        
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_destinations = sorted(destination_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analytics_data = {
            'records': records,
            'statistics': statistics,
            'user_role': user_role,
            'recent_records_count': len(recent_records),
            'monthly_data': list(sorted_monthly.values())[:12],  # Last 12 months
            'top_senders': top_senders,
            'top_destinations': top_destinations,
            'completion_rate': round((statistics.get('completed_count', 0) / max(statistics.get('total_records', 1), 1)) * 100, 1) if statistics else 0
        }
        
        return render_template('analytics.html', **analytics_data)
        
    except Exception as e:
        flash(f'Error loading analytics: {e}', 'danger')
        return redirect(url_for('home'))

@app.route('/export_tools')
@admin_required
def export_tools():
    """Export and backup tools page."""
    try:
        records = keeper.get_all_records()
        statistics = keeper.get_statistics()
        
        export_data = {
            'records': records,
            'statistics': statistics,
            'total_records': len(records)
        }
        
        return render_template('export_tools.html', **export_data)
        
    except Exception as e:
        flash(f'Error loading export tools: {e}', 'danger')
        return redirect(url_for('home'))

@app.route('/report')
@login_required
def generate_report():
    try:
        records = keeper.get_all_records()
        statistics = keeper.get_statistics()
        user_role = session.get('role', 'user')
        username = session.get('username', 'Unknown')
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate comprehensive report data
        report_data = {
            'records': records,
            'statistics': statistics,
            'user_role': user_role,
            'username': username,
            'timestamp': timestamp,
            'generated_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'total_records': len(records)
        }
        
        # Render the report template
        return render_template('report.html', **report_data)
        
    except Exception as e:
        flash(f'Error generating report: {e}', 'danger')
        return redirect(url_for('home'))

# System Settings Routes
@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Admin settings page."""
    return render_template('admin_settings.html', settings=system_settings.settings)

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Change the current user's password."""
    try:
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New password and confirmation do not match'})
        
        if auth_manager.change_password(session['username'], current_password, new_password):
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Current password is incorrect'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/change_user_password', methods=['POST'])
@admin_required
def change_user_password():
    """Change a specific user's password (admin only)."""
    try:
        target_user = request.form['target_user']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New password and confirmation do not match'})

        if auth_manager.change_user_password(target_user, new_password):
            return jsonify({'success': True, 'message': f'Password for user {target_user} changed successfully'})
        else:
            return jsonify({'success': False, 'message': f'Failed to change password for {target_user}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e) })

@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """Update system settings."""
    try:
        # Handle logo upload first if present
        if 'logo' in request.files and request.files['logo'].filename != '':
            file = request.files['logo']
            
            # Check file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # Create logos directory if it doesn't exist
                logos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'logos')
                os.makedirs(logos_dir, exist_ok=True)
                
                # Save file with secure filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(logos_dir, filename)
                file.save(filepath)
                
                # Update logo URL in settings
                logo_url = f'/uploads/logos/{filename}'
                system_settings.update_setting('logo_url', logo_url)
                flash('Logo uploaded successfully!', 'success')
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, SVG, or WebP files only.', 'warning')
        
        # Update basic settings
        if 'system_name' in request.form:
            system_settings.update_setting('system_name', request.form['system_name'])
        
        # Theme colors and typography are hardcoded for a professional appearance
        # No longer process theme field changes from the form
        
        # Update branding settings
        branding_fields = [
            'system_description', 'footer_text', 'logo_position'
        ]
        
        for field in branding_fields:
            if field in request.form:
                system_settings.update_setting(f'branding.{field}', request.form[field])
        
        # Handle checkboxes
        system_settings.update_setting('branding.show_logo', 'show_logo' in request.form)
        
        # Save settings
        if system_settings.save_settings():
            flash('System settings updated successfully!', 'success')
        else:
            flash('Failed to save settings.', 'danger')
            
    except Exception as e:
        flash(f'Error updating settings: {e}', 'danger')
    
    return redirect(url_for('admin_settings'))

@app.route('/update_record_ids', methods=['POST'])
@admin_required
def update_record_ids():
    """Update existing record IDs from old format to new format."""
    try:
        # Check if there are any records with old format
        old_format_records = [r for r in keeper.get_all_records() if r.id.startswith("LGU_TNGLN-MAYOR'S OFFICE - ")]
        
        if not old_format_records:
            return jsonify({
                'success': True, 
                'message': 'All records already use the new ID format. No updates needed.',
                'updated_count': 0
            })
        
        # Record time and sample updates for response
        import time
        start_time = time.time()
        
        # Create sample updates for feedback
        sample_updates = []
        for record in old_format_records[:5]:  # First 5 records
            old_id_parts = record.id.split(" - ")
            if len(old_id_parts) >= 2:
                number_part = old_id_parts[-1]
                new_id = f"MAYOR'S OFFICE - {number_part}"
                sample_updates.append({
                    'old_id': record.id,
                    'new_id': new_id
                })
        
        # Update the record IDs
        if keeper.update_existing_ids_to_new_format():
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            
            # Broadcast update to all connected clients
            broadcast_update("bulk_update", {
                "action": "id_format_update",
                "count": len(old_format_records),
                "total": len(old_format_records),
                "message": f"Updated {len(old_format_records)} record IDs to new format"
            })
            
            return jsonify({
                'success': True, 
                'message': f'Successfully updated {len(old_format_records)} record ID(s) to new format.',
                'updated_count': len(old_format_records),
                'time_taken': time_taken,
                'sample_updates': sample_updates
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to update record IDs. Please try again.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error updating record IDs: {str(e)}'
        })

@app.route('/get_id_update_info', methods=['GET'])
@admin_required
def get_id_update_info():
    """Get information about records that need ID format update."""
    try:
        all_records = keeper.get_all_records()
        old_format_records = [r for r in all_records if r.id.startswith("LGU_TNGLN-MAYOR'S OFFICE - ")]
        
        # Get preview of records to be updated (up to 10)
        preview_records = []
        for record in old_format_records[:10]:
            old_id_parts = record.id.split(" - ")
            if len(old_id_parts) >= 2:
                number_part = old_id_parts[-1]
                new_id = f"MAYOR'S OFFICE - {number_part}"
                preview_records.append({
                    'old_id': record.id,
                    'new_id': new_id,
                    'subject': record.subject
                })
        
        return jsonify({
            'success': True,
            'total_records': len(all_records),
            'old_format_count': len(old_format_records),
            'new_format_count': len(all_records) - len(old_format_records),
            'preview': preview_records,
            'has_more': len(old_format_records) > 10
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting ID update info: {str(e)}'
        })

@app.route('/reset_data', methods=['POST'])
@admin_required
def reset_data():
    """Reset all data in the system."""
    try:
        # Use the new reset method from RecordKeeper
        if keeper.reset_all_data():
            # Broadcast reset event to all connected clients
            broadcast_update("data_reset", {"message": "All data has been reset"})
            flash('All data has been reset successfully!', 'success')
        else:
            flash('Failed to reset data. Please try again.', 'danger')
    except Exception as e:
        flash(f'Error resetting data: {e}', 'danger')
    return redirect(url_for('admin_settings'))

@app.route('/admin/upload_logo', methods=['POST'])
@admin_required
def upload_logo():
    """Upload system logo."""
    if 'logo' not in request.files:
        flash('No logo file selected.', 'danger')
        return redirect(url_for('admin_settings'))
    
    file = request.files['logo']
    if file.filename == '':
        flash('No logo file selected.', 'danger')
        return redirect(url_for('admin_settings'))
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, SVG, or WebP files only.', 'danger')
        return redirect(url_for('admin_settings'))
    
    try:
        # Create logos directory if it doesn't exist
        logos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'logos')
        os.makedirs(logos_dir, exist_ok=True)
        
        # Save file with secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(logos_dir, filename)
        file.save(filepath)
        
        # Update logo URL in settings
        logo_url = f'/uploads/logos/{filename}'
        system_settings.update_setting('logo_url', logo_url)
        
        if system_settings.save_settings():
            flash('Logo uploaded successfully!', 'success')
        else:
            flash('Logo uploaded but failed to save settings.', 'warning')
            
    except Exception as e:
        flash(f'Error uploading logo: {e}', 'danger')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/remove_logo', methods=['POST'])
@admin_required
def remove_logo():
    """Remove system logo."""
    try:
        # Get current logo URL
        current_logo = system_settings.get_setting('logo_url', '')
        
        # Remove logo file if it exists
        if current_logo:
            logo_path = current_logo.replace('/uploads/', '')
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        # Update settings
        system_settings.update_setting('logo_url', '')
        
        if system_settings.save_settings():
            flash('Logo removed successfully!', 'success')
        else:
            flash('Failed to remove logo.', 'danger')
            
    except Exception as e:
        flash(f'Error removing logo: {e}', 'danger')
    
    return redirect(url_for('admin_settings'))

# SSE endpoint for real-time updates
@app.route('/events')
def events():
    def event_stream():
        client_id = str(uuid.uuid4())
        connected_clients.add(client_id)
        
        try:
            # Send initial connection confirmation
            yield f"data: {{\"type\": \"connected\", \"client_id\": \"{client_id}\"}}\n\n"
            
            while True:
                # Check for updates in the queue
                if not update_queue.empty():
                    try:
                        update = update_queue.get_nowait()
                        yield f"data: {json.dumps(update)}\n\n"
                    except:
                        pass
                time.sleep(0.5)  # Check every 500ms for better responsiveness
        except GeneratorExit:
            # Client disconnected
            connected_clients.discard(client_id)
        finally:
            connected_clients.discard(client_id)
    
    return Response(event_stream(), mimetype="text/event-stream")


# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Test search page
@app.route('/test_search.html')
def test_search():
    """Serve the test search page."""
    from flask import send_from_directory
    return send_from_directory('.', 'test_search.html')

# Debug search endpoint
@app.route('/debug_search')
@login_required
def debug_search():
    """Debug search endpoint with detailed logging."""
    query = request.args.get('q', '').strip()
    
    print(f"[DEBUG] Search query received: '{query}'")
    print(f"[DEBUG] Request args: {request.args}")
    print(f"[DEBUG] Request method: {request.method}")
    
    try:
        if not query:
            records = keeper.get_all_records()
            print(f"[DEBUG] No query - returning all {len(records)} records")
        else:
            records = keeper.search_records(query)
            print(f"[DEBUG] Search found {len(records)} records")
        
        # Convert records to dictionary format
        records_data = []
        for record in records:
            record_dict = {
                'id': record.id,
                'date': record.date,
                'sender': record.sender,
                'subject': record.subject,
                'destination': record.destination,
                'status': record.status
            }
            records_data.append(record_dict)
            print(f"[DEBUG] Record: {record_dict}")
        
        response_data = {
            'success': True,
            'records': records_data,
            'count': len(records_data),
            'query': query,
            'debug': {
                'total_records_in_system': len(keeper.get_all_records()),
                'search_performed': bool(query),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        print(f"[DEBUG] Returning response with {len(records_data)} records")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[DEBUG] Error in search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'query': query,
            'debug': {
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
        }), 500

if __name__ == '__main__':
    # This is only used for local development
    # In production, Gunicorn will serve the app
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
