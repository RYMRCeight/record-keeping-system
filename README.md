# 🏛️ LGU Record Keeping System

A comprehensive document management and record keeping system built with Flask, designed for Local Government Units (LGUs) and similar organizations.

## Features

- **Document Management**: Add, edit, and track documents with sender, subject, destination, and status
- **User Authentication**: Admin and user roles with different permissions
- **Real-time Updates**: Live updates using Server-Sent Events
- **Export/Import**: Support for Excel, CSV, and JSON formats
- **Analytics Dashboard**: Track statistics and trends
- **Backup & Restore**: Complete system backup functionality
- **Responsive Design**: Modern, mobile-friendly interface

## Default Login Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Regular User:**
- Username: `user`
- Password: `user123`

⚠️ **IMPORTANT**: Change these default passwords immediately after first login!

## Local Development

1. **Install Python 3.7+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python app.py
   ```
4. **Open your browser to:** `http://localhost:5000`

## Deployment to Render.com

### Prerequisites

1. **Create a GitHub account** if you don't have one
2. **Create a Render.com account** (free tier available)
3. **Install Git** on your local machine

### Step 1: Push to GitHub

1. **Install Git** from https://git-scm.com/download/win
2. **Open PowerShell/Command Prompt** in your project directory
3. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Record Keeping System"
   ```
4. **Create a new repository on GitHub:**
   - Go to https://github.com
   - Click "New repository"
   - Name it "record-keeping-system" (or your preferred name)
   - Make it public or private
   - Don't initialize with README (since you already have files)
   
5. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/record-keeping-system.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to Render.com** and sign up/log in
2. **Click "New +"** and select "Web Service"
3. **Connect your GitHub repository:**
   - Authorize Render to access your GitHub
   - Select your "record-keeping-system" repository
4. **Configure the deployment:**
   - **Name**: `record-keeping-system` (or your choice)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Plan**: Select "Free" for testing

### Step 3: Environment Variables

In the Render dashboard, add these environment variables:

- **SECRET_KEY**: Click "Generate" to create a secure secret key
- **FLASK_ENV**: Set to `production`

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (usually takes 2-5 minutes)
3. **Your app will be available** at: `https://your-service-name.onrender.com`

## Important Notes

- **File Storage**: All data is stored in JSON files, which persist on Render's free tier
- **Uploads**: User uploads are stored in the `uploads/` directory
- **Database**: This app uses file-based storage, not a traditional database
- **Real-time Features**: Server-Sent Events work well on Render

## File Structure

```
record-keeping-system/
├── app.py                 # Main Flask application
├── record_keeper.py       # Core business logic
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── start.sh              # Startup script
├── .gitignore            # Git ignore file
├── templates/            # HTML templates
├── uploads/              # File uploads directory
└── README.md             # This file
```

## Configuration Files

- **render.yaml**: Deployment configuration for Render
- **requirements.txt**: Python package dependencies
- **start.sh**: Production startup script

## Troubleshooting Render Deployment

### Common Issues:

1. **Build fails**: Check that all dependencies in `requirements.txt` are correct
2. **App won't start**: Verify the start command in Render dashboard
3. **Files not persisting**: Ensure files are being written to the correct directories

### Checking Logs:

- In Render dashboard, go to your service
- Click "Logs" to see real-time application logs
- Check for any error messages during startup

### Re-deploying:

- Any push to your main branch will trigger automatic redeployment
- Or click "Manual Deploy" in the Render dashboard

## Production Considerations

1. **Change Default Passwords**: Update admin/user passwords immediately
2. **Environment Variables**: Use secure SECRET_KEY in production
3. **File Backups**: Regularly backup your data using the built-in export features
4. **User Management**: Add proper user accounts through the admin interface

## Support

For deployment issues:
- Check Render.com documentation: https://render.com/docs
- Review application logs in Render dashboard
- Ensure all files are committed to your Git repository

## License

This project is open source and available under the [MIT License](LICENSE).
