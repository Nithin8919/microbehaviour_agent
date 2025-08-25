# 🚀 Super Duper Easy Deployment Guide

This microbehaviour analyzer can be deployed to multiple platforms with just a few clicks!

## 🔥 One-Click Deployment

```bash
chmod +x deploy/one-click-deploy.sh
./deploy/one-click-deploy.sh
```

Choose your platform and follow the prompts!

## 🌟 Quick Deploy Options

### 1. Railway (Recommended) 🚂
**Easiest & Fastest**
```bash
./deploy/deploy-to-railway.sh
```
- Free tier available
- Automatic SSL
- GitHub integration

### 2. Render 🎨
**Best for GitHub workflows**
```bash
./deploy/deploy-to-render.sh
```
- Free tier available
- Auto-deploy from Git
- Built-in SSL

### 3. Heroku 🟣
**Most popular**
```bash
./deploy/deploy-to-heroku.sh
```
- Well-established platform
- Easy scaling

### 4. Docker 🐳
**Run anywhere**
```bash
# Local deployment
docker-compose up -d

# Or build and run manually
docker build -t microbehaviour .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key microbehaviour
```

### 5. Vercel ⚡
**Serverless**
```bash
npm i -g vercel
vercel --local-config deploy/deploy-to-vercel.json
```

## 🔐 Environment Setup

1. **Copy environment template:**
   ```bash
   # Create .env file with your OpenAI API key
   echo 'OPENAI_API_KEY=your_key_here' > .env
   ```

2. **Required Environment Variables:**
   - `OPENAI_API_KEY` - Your OpenAI API key (required)
   - `PORT` - Port number (optional, default: 5000)

## 🎯 Platform-Specific Instructions

### Railway
1. Run `./deploy/deploy-to-railway.sh`
2. Follow prompts to login and create project
3. Add your OpenAI API key when prompted
4. Deploy automatically!

### Render
1. Connect your GitHub repo to Render
2. Use the `render.yaml` configuration (already included)
3. Add `OPENAI_API_KEY` environment variable
4. Deploy!

### Heroku
1. Install Heroku CLI
2. Run `./deploy/deploy-to-heroku.sh`
3. Follow prompts
4. Your app will open automatically!

### Docker
1. Install Docker and Docker Compose
2. Set `OPENAI_API_KEY` in `.env` file
3. Run `docker-compose up -d`
4. Visit `http://localhost:5000`

## 🔧 Manual Deployment

If you prefer manual setup:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY="your_key_here"
   ```

3. **Run the application:**
   ```bash
   python app/run.py
   ```

## 🌐 Production Considerations

- **SSL/HTTPS**: All cloud platforms provide automatic SSL
- **Scaling**: Railway, Render, and Heroku offer easy scaling
- **Monitoring**: Check platform dashboards for logs and metrics
- **Custom Domain**: Available on all platforms (some require paid plans)

## 🆘 Troubleshooting

**API Key Issues:**
- Ensure `OPENAI_API_KEY` is set correctly
- Check that the key has sufficient credits
- Verify the key isn't expired

**Deployment Failures:**
- Check platform logs for detailed error messages
- Ensure all dependencies in `requirements.txt` are available
- Verify Python version compatibility (3.11+ recommended)

**Performance:**
- Playwright requires sufficient memory (512MB+ recommended)
- Consider upgrading to paid tiers for better performance

## 📞 Support

If you encounter issues:
1. Check the deployment logs on your chosen platform
2. Verify environment variables are set correctly
3. Ensure your OpenAI API key is valid and has credits

Happy deploying! 🎉



