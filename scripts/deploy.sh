#!/bin/bash

###############################################################################
# Script de déploiement SmartDoc Assistant sur AWS
# Usage: ./deploy.sh [dev|prod]
###############################################################################

set -e  # Arrêt en cas d'erreur

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
STACK_NAME="smartdoc-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}
BUCKET_NAME="smartdoc-deployment-${ENVIRONMENT}-$(date +%s)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Déploiement SmartDoc Assistant${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Environnement: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Région: ${GREEN}${REGION}${NC}"
echo -e "Stack: ${GREEN}${STACK_NAME}${NC}"
echo ""

# Vérifier les prérequis
echo -e "${YELLOW}📋 Vérification des prérequis...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI n'est pas installé${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 n'est pas installé${NC}"
    exit 1
fi

if ! command -v zip &> /dev/null; then
    echo -e "${RED}❌ zip n'est pas installé${NC}"
    exit 1
fi

# Vérifier la clé API Anthropic
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ Variable d'environnement ANTHROPIC_API_KEY non définie${NC}"
    echo -e "${YELLOW}Définissez-la avec: export ANTHROPIC_API_KEY=your_key${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prérequis OK${NC}"
echo ""

# 1. Créer le bucket S3
echo -e "${YELLOW}📦 Création du bucket S3 de déploiement...${NC}"
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "Bucket existe déjà"
echo -e "${GREEN}✅ Bucket créé: ${BUCKET_NAME}${NC}"
echo ""

# 2. Package les Lambdas
echo -e "${YELLOW}📦 Package des fonctions Lambda...${NC}"

# Fonction helper pour packager une Lambda
package_lambda() {
    local AGENT_NAME=$1
    local LAMBDA_DIR="lambda/${AGENT_NAME}"
    local OUTPUT_ZIP="${AGENT_NAME}.zip"

    echo -e "  📦 Package ${AGENT_NAME}..."

    # Créer un répertoire temporaire
    TEMP_DIR=$(mktemp -d)

    # Copier les fichiers de l'agent
    cp -r ${LAMBDA_DIR}/* ${TEMP_DIR}/

    # Copier les fichiers shared
    cp -r shared/* ${TEMP_DIR}/

    # Installer les dépendances
    if [ -f "${LAMBDA_DIR}/requirements.txt" ]; then
        pip install -r ${LAMBDA_DIR}/requirements.txt -t ${TEMP_DIR}/ --quiet
    fi

    # Créer le zip
    cd ${TEMP_DIR}
    zip -r -q ${OUTPUT_ZIP} .
    mv ${OUTPUT_ZIP} ${OLDPWD}/
    cd ${OLDPWD}

    # Nettoyer
    rm -rf ${TEMP_DIR}

    echo -e "  ${GREEN}✅ ${AGENT_NAME}.zip créé${NC}"
}

# Packager chaque agent
package_lambda "orchestrator"
package_lambda "medication-agent"
package_lambda "symptom-agent"
package_lambda "emergency-agent"

echo ""

# 3. Upload vers S3
echo -e "${YELLOW}⬆️  Upload des packages vers S3...${NC}"
aws s3 cp orchestrator.zip s3://${BUCKET_NAME}/
aws s3 cp medication-agent.zip s3://${BUCKET_NAME}/
aws s3 cp symptom-agent.zip s3://${BUCKET_NAME}/
aws s3 cp emergency-agent.zip s3://${BUCKET_NAME}/
echo -e "${GREEN}✅ Packages uploadés${NC}"
echo ""

# 4. Déployer CloudFormation
echo -e "${YELLOW}🏗️  Déploiement de l'infrastructure CloudFormation...${NC}"
aws cloudformation deploy \
    --template-file infrastructure/cloudformation.yaml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        AnthropicApiKey=${ANTHROPIC_API_KEY} \
        DeploymentBucket=${BUCKET_NAME} \
        Environment=${ENVIRONMENT} \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${REGION} \
    --no-fail-on-empty-changeset

echo -e "${GREEN}✅ Infrastructure déployée${NC}"
echo ""

# 5. Récupérer l'URL de l'API
echo -e "${YELLOW}🔍 Récupération de l'URL API...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region ${REGION})

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Déploiement terminé avec succès!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}🌐 URL de l'API:${NC} ${API_URL}"
echo -e "${GREEN}📦 Bucket S3:${NC} ${BUCKET_NAME}"
echo -e "${GREEN}🏗️  Stack:${NC} ${STACK_NAME}"
echo ""
echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo -e "  1. Tester l'API: curl -X POST ${API_URL}/chat ..."
echo -e "  2. Créer des utilisateurs test"
echo -e "  3. Configurer le frontend avec cette URL"
echo ""

# Nettoyer les fichiers zip locaux
echo -e "${YELLOW}🧹 Nettoyage des fichiers temporaires...${NC}"
rm -f orchestrator.zip medication-agent.zip symptom-agent.zip emergency-agent.zip
echo -e "${GREEN}✅ Nettoyage terminé${NC}"
echo ""

echo -e "${GREEN}🎉 SmartDoc Assistant est maintenant déployé!${NC}"
