#!/bin/bash

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Build complete! Output in frontend/dist"
ls -la frontend/dist
