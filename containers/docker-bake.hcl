# 1. VARIABLE DEFINITIONS
variable "DATE" { default = "06.10.2026" }
variable "BRAINPREP_VERSION" { default = "2.2.0" }
variable "OS_VERSION" { default = "24.04" }
variable "ANTS_VERSION" { default = "2.6.5" }
variable "MORPHOLOGIST_VERSION" { default = "6.0.19" }
variable "FSLUTILS_VERSION" { default = "2412.6" }
variable "FSLFLIRT_VERSION" { default = "2111.4" }
variable "FSLDEFACE_VERSION" { default = "1.3.1" }
variable "FSLEDDY_VERSION" { default = "2602.0" }
variable "FSLDATASTANDARD_VERSION" { default = "2208.0" }
variable "CAT12_VERSION" { default = "12.9" }
variable "CAT12MCR_VERSION" { default = "R2017b" }
variable "FREESURFER_VERSION" { default = "8.2.0" }
variable "SYNTHSTRIP_VERSION" { default = "1.8" }
variable "MRIQC_VERSION" { default = "24.0.2" }
variable "FMRIPREP_VERSION" { default = "25.2.4" }
variable "MRTRIX3_VERSION" { default = "26965d" }
variable "GEOLAB_VERSION" { default = "f5de43" }
variable "TRACTSEG_VERSION" { default = "2.10" }
variable "SYNB0_VERSION" { default = "v3" }
variable "AMICO_VERSION" { default = "2.1.1" }

# 2. CONFIGURATIONS
variable "global_args" {
    default = {
        DATE                    = DATE
        BRAINPREP_VERSION       = BRAINPREP_VERSION
        OS_VERSION              = OS_VERSION
        ANTS_VERSION            = ANTS_VERSION
        MORPHOLOGIST_VERSION    = MORPHOLOGIST_VERSION
        FSLUTILS_VERSION        = FSLUTILS_VERSION
        FSLFLIRT_VERSION        = FSLFLIRT_VERSION
        FSLDEFACE_VERSION       = FSLDEFACE_VERSION
        FSLEDDY_VERSION         = FSLEDDY_VERSION
        FSLDATASTANDARD_VERSION = FSLDATASTANDARD_VERSION
        CAT12_VERSION           = CAT12_VERSION
        CAT12MCR_VERSION        = CAT12MCR_VERSION
        FREESURFER_VERSION      = FREESURFER_VERSION
        SYNTHSTRIP_VERSION      = SYNTHSTRIP_VERSION
        MRIQC_VERSION           = MRIQC_VERSION
        FMRIPREP_VERSION        = FMRIPREP_VERSION
        MRTRIX3_VERSION         = MRTRIX3_VERSION
        GEOLAB_VERSION          = GEOLAB_VERSION
        TRACTSEG_VERSION        = TRACTSEG_VERSION
        SYNB0_VERSION           = SYNB0_VERSION
        AMICO_VERSION           = AMICO_VERSION
    }
}
variable "global_labels" {
    default = {
        "org.opencontainers.image.title" = "brainprep"
        "org.opencontainers.image.version" = "${BRAINPREP_VERSION}"
        "org.opencontainers.image.licenses" = "CeCILL-B"
        "org.opencontainers.image.authors" = "brainprepdesk team"
        "org.opencontainers.image.documentation" = "https://brainprepdesk.github.io/brainprep/stable"
        "org.opencontainers.image.source" = "https://github.com/brainprepdesk/brainprep"
        "org.opencontainers.image.created" = "${DATE}"
    }
}
variable "target_configs" {
    default = {

        # Installers
        "base": {
            stage = "base"
            tag = "base"
        }
        "ants-installer": {
            stage = "ants-installer"
            extra_labels = {
                "com.brainprep.ants.version" = "${ANTS_VERSION}"
            }
            tag = "ant"
        }
        "morphologist-installer": {
            stage = "morphologist-installer"
            extra_labels = {
                "com.brainprep.morphologist.version" = "${MORPHOLOGIST_VERSION}"
            }
            tag = "morphologist"
        }
        "fsl-installer": {
            stage = "fsl-installer"
            extra_labels = {
                "com.brainprep.fslutils.version" = "${FSLUTILS_VERSION}"
                "com.brainprep.fslflirt.version" = "${FSLFLIRT_VERSION}"
                "com.brainprep.fsldeface.version" = "${FSLDEFACE_VERSION}"
                "com.brainprep.fsleddy.version" = "${FSLEDDY_VERSION}"
                "com.brainprep.fsldatastandard.version" = "${FSLDATASTANDARD_VERSION}"
            }
            tag = "fsl"
        }
        "synthstrip-installer": {
            stage = "synthstrip-installer"
            extra_labels = {
                "com.brainprep.synthstrip.version" = "${SYNTHSTRIP_VERSION}"
            }
            tag ="synthstrip"
        }
        "cat12-installer" = {
            stage = "cat12-installer"
            extra_labels = {
                "com.brainprep.cat12.version" = "${CAT12_VERSION}"
            }
            tag = "cat12"
        }
        "freesurfer-installer": {
            stage = "freesurfer-installer"
            extra_labels = {
                "com.brainprep.freesurfer.version" = "${FREESURFER_VERSION}"
            }
            tag = "freesurfer"
        }
        "mrtrix3-installer": {
            stage = "mrtrix3-installer"
            extra_labels = {
                "com.brainprep.mrtrix3.version" = "${MRTRIX3_VERSION}"
            }
            tag = "mrtrix3"
        }
        "tractseg-installer": {
            stage = "tractseg-installer"
            extra_labels = {
                "com.brainprep.tractseg.version" = "${TRACTSEG_VERSION}"
            }
            tag = "tractseg"
        }
        "geolab-installer": {
            stage = "geolab-installer"
            extra_labels = {
                "com.brainprep.geolab.version" = "${GEOLAB_VERSION}"
            }
            tag = "geolab"
        }
        "synb0-installer": {
            stage = "synb0-installer"
            extra_labels = {
                "com.brainprep.synb0.version" = "${SYNB0_VERSION}"
            }
            tag = "synb0"
        }

        # Downloaders
        "mni512-downloader": {
            stage = "mni512-downloader"
            tag = "mni512data"
        }
        "adhd200-downloader": {
            stage = "adhd200-downloader"
            tag = "adhd200data"
        }

        # Workflows
        "brainprep-quality_assurance": {
            dockerfile = "Dockerfile.quality_assurance"
            extra_labels = {
                "com.brainprep.mriqc.version" = "${MRIQC_VERSION}"
            }
            tag = "quality_assurance"
        }
        "brainprep-fmriprep": {
            dockerfile = "Dockerfile.fmriprep"
            extra_labels = {
                "com.brainprep.fmriprep.version" = "${FMRIPREP_VERSION}"
            }
            tag = "fmriprep"
        }
        "brainprep-defacing": {
            dockerfile = "Dockerfile.defacing"
            contexts = {
                base = "target:base"
                synthstrip-installer = "target:synthstrip-installer"
                fsl-installer = "target:fsl-installer"
            }
            extra_args = {
                BASE_IMAGE = "base"
            }
            extra_labels = {
                "com.brainprep.fsldeface.version" = "${FSLDEFACE_VERSION}"
            }
            tag = "defacing"
        }
        "brainprep-quasiraw": {
            dockerfile = "Dockerfile.quasiraw"
            contexts = {
                base = "target:base"
                synthstrip-installer = "target:synthstrip-installer"
                ants-installer = "target:ants-installer"
                fsl-installer = "target:fsl-installer"
            }
            extra_args = {
                BASE_IMAGE = "base"
            }
            extra_labels = {
                "com.brainprep.fslutils.version" = "${FSLUTILS_VERSION}"
                "com.brainprep.fslflirt.version" = "${FSLFLIRT_VERSION}"
                "com.brainprep.synthstrip.version" = "${SYNTHSTRIP_VERSION}"
                "com.brainprep.ants.version" = "${ANTS_VERSION}"
            }
            tag = "quasiraw"
        }
        "brainprep-sulcirec": {
            dockerfile = "Dockerfile.sulcirec"
            contexts = {
                base = "target:base"
                morphologist-installer = "target:morphologist-installer"
            }
            extra_args = {
                BASE_IMAGE = "base"
            }
            extra_labels = {
                "com.brainprep.morphologist.version" = "${MORPHOLOGIST_VERSION}"
            }
            tag = "sulcirec"
        }
        "brainprep-vbm" = {
            dockerfile = "Dockerfile.vbm"
            contexts = {
                base = "target:base"
                cat12-installer = "target:cat12-installer"
            }
            extra_args = {
                BASE_IMAGE = "base"
            }
            extra_labels = {
                "com.brainprep.cat12.version" = "${CAT12_VERSION}"
            }
            tag = "vbm"
        }
        "brainprep-dmriprep" = {
            dockerfile = "Dockerfile.dmriprep"
            contexts = {
                base = "target:base"
                fsl-installer = "target:fsl-installer"
                synthstrip-installer = "target:synthstrip-installer"
                ants-installer = "target:ants-installer"
                mrtrix3-installer = "target:mrtrix3-installer"
                geolab-installer = "target:geolab-installer"
                tractseg-installer = "target:tractseg-installer"
                synb0-installer = "target:synb0-installer"
                mni512-downloader = "target:mni512-downloader"
                adhd200-downloader = "target:adhd200-downloader"
            }
            extra_args = {
                BASE_IMAGE = "base"
            }
            extra_labels = {
                "com.brainprep.fslutils.version" = "${FSLUTILS_VERSION}"
                "com.brainprep.fslflirt.version" = "${FSLFLIRT_VERSION}"
                "com.brainprep.fsleddy.version" = "${FSLEDDY_VERSION}"
                "com.brainprep.fsldatastandard.version" = "${FSLDATASTANDARD_VERSION}"
                "com.brainprep.synthstrip.version" = "${SYNTHSTRIP_VERSION}"
                "com.brainprep.ants.version" = "${ANTS_VERSION}"
                "com.brainprep.mrtrix3.version" = "${MRTRIX3_VERSION}"
                "com.brainprep.geolab.version" = "${GEOLAB_VERSION}"
                "com.brainprep.tractseg.version" = "${TRACTSEG_VERSION}"
                "com.brainprep.synb0.version" = "${SYNB0_VERSION}"
                "com.brainprep.amico.version" = "${AMICO_VERSION}"
            }
            tag = "dmriprep"
        }
    }
}

# 3. DYNAMIC TARGETS GENERATION
target "app" {
    matrix = {
        service = keys(target_configs)
    }
    name = "${service}"
    dockerfile = lookup(target_configs[service], "dockerfile", "Dockerfile.stages")
    contexts = lookup(target_configs[service], "contexts", {})
    target = can(target_configs[service].stage) ? target_configs[service].stage : null
    tags = ["brainprep-${target_configs[service].tag}:${BRAINPREP_VERSION}"]
    args = merge(
        global_args,
        lookup(target_configs[service], "extra_args", {})
    )
    labels = merge(
        global_labels,
        lookup(target_configs[service], "extra_labels", {})
    )
}     

# 4. GROUPS
group "default" {
    targets = keys(target_configs)
}
