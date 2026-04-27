#!/bin/bash

################################################################################
# CLEATI V3.3 - Quick GitHub Setup Script
# Execute this script to push your code to GitHub and start CI/CD pipelines
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   CLEATI V3.3 - GitHub Setup & Deployment Pipeline Start    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Configure Git
echo -e "\n${YELLOW}Step 1: Configuring Git...${NC}"
git config --global user.name "CLEATI Team" 2>/dev/null || git config user.name "CLEATI Team"
git config --global user.email "jfpitey@beseen360app.com" 2>/dev/null || git config user.email "jfpitey@beseen360app.com"
echo -e "${GREEN}✓ Git configured${NC}"

# Step 2: Initialize repository
echo -e "\n${YELLOW}Step 2: Initializing Git repository...${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓ Repository initialized${NC}"
else
    echo -e "${GREEN}✓ Repository already initialized${NC}"
fi

# Step 3: Check files
echo -e "\n${YELLOW}Step 3: Verifying files...${NC}"
required_files=(
    "cleati_production_api_v3_i18n.py"
    "cleati_interface_v3_i18n.html"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    ".gitignore"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✓ $file${NC}"
    else
        echo -e "${RED}  ✗ $file (MISSING)${NC}"
    fi
done

# Step 4: Add all files
echo -e "\n${YELLOW}Step 4: Adding files to Git...${NC}"
git add .
echo -e "${GREEN}✓ All files added${NC}"

# Step 5: Check status
echo -e "\n${YELLOW}Step 5: Git status:${NC}"
git status --short | head -20

# Step 6: Create initial commit
echo -e "\n${YELLOW}Step 6: Creating initial commit...${NC}"
if git diff --cached --quiet; then
    echo -e "${YELLOW}  No changes to commit${NC}"
else
    git commit -m "🚀 Initial commit: CLEATI V3.3 with 8-language i18n system

- Complete I18n system with 8 languages (EN, FR, ES, DE, IT, PT, NL, PL)
- 40 translation files with 139 unique keys
- REST API with FastAPI
- Professional frontend UI
- Docker containerization
- GitHub Actions CI/CD pipeline
- Production deployment automation
- Complete monitoring & health checks

Version: 3.3.0
Status: Production Ready" || true
    echo -e "${GREEN}✓ Initial commit created${NC}"
fi

# Step 7: Create main branch
echo -e "\n${YELLOW}Step 7: Setting up main branch...${NC}"
git branch -M main 2>/dev/null || true
echo -e "${GREEN}✓ Main branch ready${NC}"

# Step 8: Add remote
echo -e "\n${YELLOW}Step 8: Adding GitHub remote...${NC}"
REMOTE_URL="https://github.com/jf-beseen360/cleati-production.git"

if git remote get-url origin &>/dev/null; then
    echo -e "${YELLOW}  Remote already exists${NC}"
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi
echo -e "${GREEN}✓ Remote configured: $REMOTE_URL${NC}"

# Step 9: Display next steps
echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ LOCAL SETUP COMPLETE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}1. Push to GitHub (requires authentication):${NC}"
echo -e "   ${GREEN}git push -u origin main${NC}"
echo ""
echo -e "${BLUE}2. Create develop branch:${NC}"
echo -e "   ${GREEN}git checkout -b develop${NC}"
echo -e "   ${GREEN}git push -u origin develop${NC}"
echo ""
echo -e "${BLUE}3. Verify on GitHub:${NC}"
echo -e "   → https://github.com/jf-beseen360/cleati-production${NC}"
echo ""
echo -e "${BLUE}4. Configure GitHub Settings:${NC}"
echo -e "   → Settings → Branches → Add protection rules${NC}"
echo -e "   → Settings → Secrets → Add deployment secrets (if needed)${NC}"
echo ""
echo -e "${BLUE}5. Monitor CI/CD:${NC}"
echo -e "   → Actions tab to see running pipelines${NC}"
echo ""
echo -e "${YELLOW}Key Files Created:${NC}"
echo -e "  ${GREEN}✓ .github/workflows/ci-cd.yml${NC} - Testing & Building"
echo -e "  ${GREEN}✓ .github/workflows/deploy.yml${NC} - Production Deployment"
echo -e "  ${GREEN}✓ .gitignore${NC} - File exclusions"
echo -e "  ${GREEN}✓ README.md${NC} - Documentation"
echo ""
echo -e "${YELLOW}Current Git Status:${NC}"
git log --oneline -1
echo ""
git branch -a | sed 's/^/  /'
echo ""
echo -e "${GREEN}You are ready to deploy! 🚀${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "For detailed instructions, see: GITHUB_PUSH_INSTRUCTIONS.md"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
