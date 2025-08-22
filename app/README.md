# Microbehavior Analyzer - Professional Frontend

This is a beautiful, professional-looking web frontend for the Microbehavior Analyzer, built with Flask and modern web technologies.

## Features

- 🎨 **Modern Design**: Beautiful gradient backgrounds, smooth animations, and professional color scheme
- 📱 **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- 🚀 **Fast Performance**: Lightweight and optimized for speed
- 🔍 **Interactive Analysis**: Real-time analysis with beautiful visualizations
- 📊 **Data Visualization**: Clean tables, progress bars, and metrics display
- 🎯 **User Experience**: Intuitive interface with smooth transitions and feedback

## Color Scheme

The application uses a professional color palette:
- **Primary**: Indigo (#6366f1) - Main actions and highlights
- **Secondary**: Purple (#8b5cf6) - Secondary elements and accents
- **Accent**: Cyan (#06b6d4) - Information and data visualization
- **Success**: Emerald (#10b981) - Positive indicators
- **Warning**: Amber (#f59e0b) - Caution indicators
- **Error**: Red (#ef4444) - Error states

## Getting Started

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

### Running the Application

1. **Activate your virtual environment** (if using one):
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. **Set your OpenAI API key** in a `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Run the Flask application**:
   ```bash
   cd app
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Enter a URL**: Input the website you want to analyze
2. **Set Business Goal** (optional): Specify what you want users to accomplish
3. **Choose AI Model**: Select from available OpenAI models
4. **Click Analyze**: The system will crawl the site and generate insights
5. **Review Results**: Explore the analysis through different tabs:
   - **Overview**: Top microbehaviors in a sortable table
   - **Timeline**: User journey stages with detailed breakdowns
   - **Raw Data**: Complete JSON response for technical analysis

## Architecture

- **Backend**: Flask web framework with RESTful API
- **Frontend**: Modern HTML5, CSS3, and vanilla JavaScript
- **Styling**: Custom CSS with CSS Grid, Flexbox, and CSS Variables
- **Icons**: Font Awesome for professional iconography
- **Fonts**: Inter font family for excellent readability

## Customization

### Colors
Modify the CSS variables in the `:root` selector to change the color scheme:

```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* ... other colors */
}
```

### Layout
The application uses CSS Grid and Flexbox for responsive layouts. Modify the grid templates and flex properties to adjust the layout.

### Animations
Customize animations by modifying the CSS keyframes and transition properties.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Optimized CSS with minimal repaints
- Efficient JavaScript with event delegation
- Responsive images and lazy loading where applicable
- Minimal external dependencies

## Security

- Input validation on both client and server side
- CSRF protection (can be added if needed)
- Secure headers and content security policies
- Environment variable management for sensitive data

## Deployment

The application can be deployed to various platforms:

- **Heroku**: Add a `Procfile` and deploy
- **AWS**: Use Elastic Beanstalk or EC2
- **Google Cloud**: App Engine or Compute Engine
- **Docker**: Containerize and deploy anywhere

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`
2. **API key not found**: Ensure `.env` file exists and contains `OPENAI_API_KEY`
3. **Analysis fails**: Check the console for error messages and verify the URL is accessible

### Debug Mode

For development, the app runs in debug mode by default. For production, set `debug=False` in `app.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Microbehavior Analyzer suite.
