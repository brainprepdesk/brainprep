#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, 
# and treat unset variables as an error.
set -euo pipefail

# --- COLOR DEFINITIONS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- CONFIGURATION ---
BAKE_FILE="docker-bake.hcl"
OUTPUT_DIR="./images"
TMP_BUILD_DIR="${OUTPUT_DIR}/tmp"
CACHE_BUILD_DIR="${OUTPUT_DIR}/cache"
BRAINPREP_VERSION="2.2.0"
# Define the array of image tags to export
IMAGES=(
    #"brainprep-ants:${BRAINPREP_VERSION}"
    #"brainprep-morphologist:${BRAINPREP_VERSION}"
    #"brainprep-fsl:${BRAINPREP_VERSION}"
    #"brainprep-synthstrip:${BRAINPREP_VERSION}"
    #"brainprep-cat12:${BRAINPREP_VERSION}"
    #"brainprep-freesurfer:${BRAINPREP_VERSION}"
    #"brainprep-mrtrix3:${BRAINPREP_VERSION}"
    #"brainprep-tractseg:${BRAINPREP_VERSION}"
    #"brainprep-geolab:${BRAINPREP_VERSION}"
    #"brainprep-synb0:${BRAINPREP_VERSION}"
    #"brainprep-quality_assurance:${BRAINPREP_VERSION}"
    #"brainprep-fmriprep:${BRAINPREP_VERSION}"
    #"brainprep-defacing:${BRAINPREP_VERSION}"
    #"brainprep-quasiraw:${BRAINPREP_VERSION}"
    #"brainprep-sulcirec:${BRAINPREP_VERSION}"
    #"brainprep-vbm:${BRAINPREP_VERSION}"
    #"brainprep-sbm:${BRAINPREP_VERSION}"
    "brainprep-dmriprep:${BRAINPREP_VERSION}"
)

# --- Welcome banner ---
echo -e "${CYAN}====================================================================${NC}"
echo -e "${YELLOW}   WELCOME TO THE AUTOMATED DOCKER-TO-APPTAINER FACTORY PIPELINE  ${NC}"
echo -e "${CYAN}====================================================================${NC}"
echo -e "${BLUE}⏱️  Starting pipeline execution at:${NC} $(date)"
echo -e "${BLUE}📦 Target images scheduled for conversion:${NC}"
for IMG in "${IMAGES[@]}"; do
    echo -e "   • ${YELLOW}${IMG}${NC}"
done
echo -e "${CYAN}====================================================================${NC}"
echo ""

# --- STEP 1: Initialization ---
echo -e "${BLUE}[1/4] ⚙️ Initializing workspace configuration...${NC}"
mkdir -p "${TMP_BUILD_DIR}"
mkdir -p "${CACHE_BUILD_DIR}"
export APPTAINER_TMPDIR="$(realpath "${TMP_BUILD_DIR}")"
export APPTAINER_CACHEDIR="$(realpath "${CACHE_BUILD_DIR}")"
echo -e "-> APPTAINER_TMPDIR   = ${YELLOW}${APPTAINER_TMPDIR}${NC}"
echo -e "-> APPTAINER_CACHEDIR = ${YELLOW}${APPTAINER_CACHEDIR}${NC}"
echo -e "${GREEN} Storage directories successfully redirected.${NC}"
# Verify if the bake JSON configuration file exists
if [ ! -f "$BAKE_FILE" ]; then
    echo "❌ Error: $BAKE_FILE not found in the current directory." >&2
    exit 1
fi
# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: 'docker' is missing.${NC}" >&2
    exit 1
fi
# Check if apptainer is installed
if ! command -v apptainer &> /dev/null; then
    echo -e "${RED}❌ Error: 'apptainer' is missing.${NC}" >&2
    exit 1
fi
echo -e "${GREEN} Workspace and requirements verified.${NC}\n"

# --- STEP 2: Build & Load ---
echo -e "${BLUE}[2/4] 🏗️ Compiling targets via Buildx Bake...${NC}"
docker buildx bake -f "$BAKE_FILE" --load
echo -e "${GREEN} Bake process completed and loaded successfully.${NC}\n"

# --- STEP 3: Export One Tar Per Image ---
echo -e "${BLUE}[3/4] 📦 Exporting images...${NC}"

for IMAGE in "${IMAGES[@]}"; do
    # Extract the image name and the tag separately
    NAME=$(echo "${IMAGE}" | cut -d':' -f1)
    TAG=$(echo "${IMAGE}" | cut -d':' -f2)
    
    # Define file paths
    TAR_PATH="${OUTPUT_DIR}/${NAME}-v${TAG}.tar"
    SIF_PATH="${OUTPUT_DIR}/${NAME}-v${TAG}.sif"

    echo -e "${CYAN}----------------------------------------------------------------${NC}"
    echo -e "  🔄 Processing Image: ${YELLOW}${IMAGE}${NC}"
    echo -e "${CYAN}----------------------------------------------------------------${NC}"
    
    
    echo -e "💾 [1/2] Saving Docker image ${IMAGE} to ${TAR_PATH}..."
    docker save -o "${TAR_PATH}" "${IMAGE}"

    echo -e "💾 [2/2] Importing Docker image ${TAR_PATH} to ${SIF_PATH}..."
    apptainer build --force "${SIF_PATH}" "docker-archive://$(realpath "${TAR_PATH}")"

done

# --- STEP 4: Post-Build Cleanup & Summary ---
echo -e "${BLUE}[4/4] Performing pipeline wrap up routines...${NC}"
rm -rf "${TMP_BUILD_DIR}"
rm -rf "${CACHE_BUILD_DIR}"
echo -e "${GREEN}✓ Environment path storage cleared.${NC}\n"

# -- Goodbye banner ---
echo -e "${CYAN}====================================================================${NC}"
echo -e "${GREEN} ✅ ALL CONVERSION PIPELINE JOBS COMPLETED SUCCESSFULLY!${NC}"
echo -e "${CYAN}====================================================================${NC}"
echo -e "${BLUE}📊 Final Docker images built:${NC}"
ls -lh "${OUTPUT_DIR}"/*.tar
echo -e "${BLUE}📊 Final Apptainer images built:${NC}"
ls -lh "${OUTPUT_DIR}"/*.sif
echo -e "${GREEN}🚀 Ready to use BrainPrep 🚀${NC}"
