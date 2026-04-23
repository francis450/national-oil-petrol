#!/bin/bash
# Script to build National Oil frontend and update petrol.html with latest assets

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
WWW_DIR="$SCRIPT_DIR/national_oil/www"
PUBLIC_DIST_DIR="$SCRIPT_DIR/national_oil/public/frontend/dist"

echo "Building National Oil frontend..."
rm -rf "$PUBLIC_DIST_DIR"
cd "$FRONTEND_DIR" && npm run build

if [ $? -eq 0 ]; then
    echo "Build successful! Frontend assets written to public dist."
    
    echo "Updating petrol.html..."
    
    # Get the actual asset filenames from served public dist
    JS_FILE=$(find "$PUBLIC_DIST_DIR/assets" -maxdepth 1 -name 'index-*.js' -print | head -1 | xargs -n1 basename)
    CSS_FILE=$(find "$PUBLIC_DIST_DIR/assets" -maxdepth 1 -name 'index-*.css' -print | head -1 | xargs -n1 basename)
    
    if [ -z "$JS_FILE" ] || [ -z "$CSS_FILE" ]; then
        echo "✗ Could not find built assets!"
        exit 1
    fi
    
    # Copy the built index.html to petrol.html with Jinja raw tags and CSRF token
    echo "{% raw %}" > "$WWW_DIR/petrol.html"
    
    # Add header with corrected asset paths
    cat >> "$WWW_DIR/petrol.html" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>National Oil - Petrol Station Management</title>
HTMLEOF
    
    # Add CSS link with correct path
    echo "    <link rel=\"stylesheet\" crossorigin href=\"/assets/national_oil/frontend/dist/assets/$CSS_FILE\">" >> "$WWW_DIR/petrol.html"
    
    # Add closing head and app div
    cat >> "$WWW_DIR/petrol.html" << 'HTMLEOF'
  </head>
  <body class="bg-chronos-black text-white">
    <div id="app"></div>
HTMLEOF
    
    echo "{% endraw %}" >> "$WWW_DIR/petrol.html"
    
    # Add JS script with correct path
    cat >> "$WWW_DIR/petrol.html" << HTMLEOF
    <script type="module" crossorigin src="/assets/national_oil/frontend/dist/assets/$JS_FILE"></script>
    <script>
      // Set CSRF token and session user from Jinja template
      window.csrf_token = '{{ frappe.session.csrf_token }}';
      window.currentUser = '{{ frappe.session.user }}';
      
      if (window.csrf_token) {
        document.cookie = 'csrf_token=' + encodeURIComponent(window.csrf_token) + '; path=/';
      }
      
      console.log('Session initialized. Current user:', window.currentUser);
    </script>
  </body>
</html>
HTMLEOF
    
    echo "✓ petrol.html updated successfully!"
    echo "✓ Assets available at: $PUBLIC_DIST_DIR/"
    echo "Run 'bench clear-cache && bench restart' to apply changes."
else
    echo "✗ Build failed!"
    exit 1
fi
