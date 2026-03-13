# Frontend Setup Instructions

The frontend requires Node.js and npm to be installed on your system.

## Install Node.js

### macOS (using Homebrew)
```bash
brew install node
```

### macOS (using MacPorts)
```bash
sudo port install nodejs
```

### macOS (manual download)
Visit https://nodejs.org and download the LTS version

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Windows
Visit https://nodejs.org and download the LTS installer

## Install Frontend Dependencies

Once Node.js is installed:

```bash
cd frontend
npm install
npm run dev
```

This will install all required packages:
- React
- React Router
- React Query
- TypeScript
- Tailwind CSS
- Lucide React Icons
- And other dependencies

## Verify Installation

```bash
npm --version  # Should show npm version
node --version # Should show node version
```

## Frontend Access

Once npm install is complete and you run `npm run dev`, the frontend will be available at:
- http://localhost:5173 (or the port shown in terminal)

## Troubleshooting

If you encounter errors:
1. Delete `node_modules` folder: `rm -rf node_modules`
2. Clear npm cache: `npm cache clean --force`
3. Try again: `npm install`
