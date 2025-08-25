#!/bin/bash

echo "Building Microbehaviour Frontend..."

# Create build directory
mkdir -p build

# Copy static files
cp -r static/* build/ 2>/dev/null || true
cp -r screenshots/* build/ 2>/dev/null || true

# Copy HTML templates
cp *.html build/ 2>/dev/null || true

# Create a simple index.html if none exists
if [ ! -f build/index.html ]; then
    echo "Creating default index.html..."
    cat > build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microbehaviour Analysis Tool</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>Microbehaviour Analysis Tool</h1>
        <p>Frontend is ready for deployment.</p>
    </div>
</body>
</html>
EOF
fi

echo "Frontend build complete! Files are in the 'build' directory."
