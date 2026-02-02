<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import * as faceapi from 'face-api.js'
import { onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import rectangle from '@/core/assets/rectangle.png'
import triangle from '@/core/assets/triangle.png'
import trapezoid from '@/core/assets/trapezoid.png'
import oval from '@/core/assets/oval.png'
import invertedTriangle from '@/core/assets/inverted-triangle.png'

const router = useRouter()

const weightKg = ref('')
const heightCm = ref('')
const bodyTypes = ['RECTANGLE', 'TRIANGLE', 'TRAPEZOID', 'OVAL', 'INVERTED_TRIANGLE'] as const
const bodtTypeImages = {
  RECTANGLE: rectangle,
  TRIANGLE: triangle,
  TRAPEZOID: trapezoid,
  OVAL: oval,
  INVERTED_TRIANGLE: invertedTriangle,
}

type BodyType = (typeof bodyTypes)[number]

const bodyType = ref<BodyType | ''>('')
const faceImage = ref('')

const step = ref<1 | 2 | 3>(1)

// Face Detection State
const videoEl = ref<HTMLVideoElement | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)
const isLoadingModels = ref(false)
const isFaceDetected = ref(false)
const detectionStatus = ref<'SEARCHING' | 'MULTIPLE_FACES' | 'TOO_FAR' | 'TOO_CLOSE' | 'PERFECT'>(
  'SEARCHING',
)
let detectionInterval: number | null = null

type PhysicalRequestDTO = {
  weightKg: number
  heightCm: number
  bodyType: BodyType
  faceImage: string
}

const bodyTypeLabels: Record<BodyType, string> = {
  RECTANGLE: 'Rectangle',
  TRIANGLE: 'Triangle',
  TRAPEZOID: 'Trapezoid',
  OVAL: 'Oval',
  INVERTED_TRIANGLE: 'Inverted triangle',
}

const goNextFromMeasures = () => {
  const weight = Number(weightKg.value)
  const height = Number(heightCm.value)

  if (!weight || weight <= 0 || !height || height <= 0) return
  step.value = 2
}

const goNextFromBodyType = () => {
  if (!bodyType.value) return
  step.value = 3
}

// Face API Logic
const loadModels = async () => {
  isLoadingModels.value = true
  try {
    const MODEL_URL = '/models'
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
      faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
      faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
    ])
    startVideo()
  } catch (error) {
    console.error('Error loading models:', error)
  } finally {
    isLoadingModels.value = false
  }
}

const startVideo = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { width: 1280, height: 720 } })
    .then((stream) => {
      if (videoEl.value) {
        videoEl.value.srcObject = stream
      }
    })
    .catch((err) => console.error('Error starting video:', err))
}

const onPlay = () => {
  if (!videoEl.value || !canvasEl.value) return

  const displaySize = {
    width: videoEl.value.videoWidth || 640,
    height: videoEl.value.videoHeight || 480,
  }

  // Match canvas size to video
  faceapi.matchDimensions(canvasEl.value, displaySize)

  detectionInterval = window.setInterval(async () => {
    if (!videoEl.value || !canvasEl.value) return

    const detections = await faceapi.detectAllFaces(
      videoEl.value,
      new faceapi.TinyFaceDetectorOptions(),
    )

    const resizedDetections = faceapi.resizeResults(detections, displaySize)

    // Clear canvas - we don't draw detections anymore, but keep it cleared
    const ctx = canvasEl.value.getContext('2d')
    ctx?.clearRect(0, 0, canvasEl.value.width, canvasEl.value.height)

    // Analyze detections
    if (resizedDetections.length === 0) {
      detectionStatus.value = 'SEARCHING'
      isFaceDetected.value = false
    } else if (resizedDetections.length > 1) {
      detectionStatus.value = 'MULTIPLE_FACES'
      isFaceDetected.value = false
    } else {
      const face = resizedDetections[0]
      const faceWidth = face.box.width
      const canvasWidth = canvasEl.value.width

      // Calculate face coverage percentage
      const coverage = (faceWidth / canvasWidth) * 100

      if (coverage < 15) {
        detectionStatus.value = 'TOO_FAR'
        isFaceDetected.value = false
      } else if (coverage > 60) {
        detectionStatus.value = 'TOO_CLOSE'
        isFaceDetected.value = false
      } else {
        detectionStatus.value = 'PERFECT'
        isFaceDetected.value = true
      }
    }
  }, 200) // Check every 200ms
}

const capturePhoto = () => {
  if (!videoEl.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoEl.value.videoWidth
  canvas.height = videoEl.value.videoHeight
  const ctx = canvas.getContext('2d')

  if (ctx) {
    // Draw raw video frame without mirroring
    ctx.drawImage(videoEl.value, 0, 0)
    faceImage.value = canvas.toDataURL('image/png')

    // Stop detection
    if (detectionInterval) clearInterval(detectionInterval)
  }
}

const retakePhoto = () => {
  faceImage.value = ''
  onPlay() // Restart detection
}

// Watch for step change to initialize camera
watch(step, (newStep) => {
  if (newStep === 3) {
    loadModels()
  } else {
    // Stop video if leaving step 3
    if (videoEl.value && videoEl.value.srcObject) {
      const stream = videoEl.value.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
    }
    if (detectionInterval) clearInterval(detectionInterval)
  }
})

onBeforeUnmount(() => {
  if (detectionInterval) clearInterval(detectionInterval)
  if (videoEl.value && videoEl.value.srcObject) {
    const stream = videoEl.value.srcObject as MediaStream
    stream.getTracks().forEach((track) => track.stop())
  }
})

const handleSubmit = () => {
  const weight = Number(weightKg.value)
  const height = Number(heightCm.value)

  if (!weight || weight <= 0) return
  if (!height || height <= 0) return
  if (!bodyType.value) return
  if (!faceImage.value) return

  const payload: PhysicalRequestDTO = {
    weightKg: weight,
    heightCm: height,
    bodyType: bodyType.value,
    faceImage: faceImage.value,
  }

  console.log('PhysicalRequestDTO', payload)
  router.push('/onboarding/interview')
}
</script>

<template>
  <div class="min-h-screen w-full flex flex-col bg-white relative overflow-hidden">
    <!-- Floating orbs -->
    <div
      class="absolute -top-32 -left-32 size-96 opacity-30 blur-3xl rounded-full bg-primary"
    ></div>
    <div
      class="absolute top-40 right-32 size-96 opacity-30 blur-3xl rounded-full bg-blue-300"
    ></div>
    <div
      class="absolute bottom-32 right-20 size-96 opacity-30 blur-3xl rounded-full bg-primary/60"
    ></div>
    <div
      class="absolute bottom-20 left-40 size-96 opacity-30 blur-3xl rounded-full bg-blue-400"
    ></div>

    <!-- Logo -->
    <div class="absolute top-8 left-8 z-10">
      <span class="text-[28px] font-bold text-black">Altai</span>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex items-center justify-center px-8 relative z-10">
      <div class="w-full max-w-5xl space-y-10">
        <Transition name="fade-step" mode="out-in">
          <!-- STEP 1: WEIGHT & HEIGHT -->
          <div v-if="step === 1" key="step-measures" class="space-y-10 max-w-3xl mx-auto">
            <div class="space-y-3">
              <label class="text-[24px] text-slate-900 font-semibold"> Physical measures </label>

              <div class="space-y-6 mt-2">
                <div class="space-y-2">
                  <span class="text-sm text-slate-600">Weight (kg)</span>
                  <input
                    v-model="weightKg"
                    type="number"
                    inputmode="decimal"
                    min="0"
                    placeholder="Enter your weight in kg"
                    class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors"
                  />
                </div>

                <div class="space-y-2">
                  <span class="text-sm text-slate-600">Height (cm)</span>
                  <input
                    v-model="heightCm"
                    type="number"
                    inputmode="decimal"
                    min="0"
                    placeholder="Enter your height in cm"
                    @keyup.enter="goNextFromMeasures"
                    class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors"
                  />
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="goNextFromMeasures"
                  :disabled="!Number(weightKg) || !Number(heightCm)"
                  class="text-[20px] px-10 py-6 tracking-wide disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Next
                </Button>
                <span class="text-[14px] text-slate-500">
                  press <span class="font-mono font-medium">Enter ↵</span>
                </span>
              </div>
            </div>
          </div>

          <!-- STEP 2: BODY TYPE -->
          <div v-else-if="step === 2" key="step-bodytype" class="space-y-10 max-w-3xl mx-auto">
            <div>
              <label class="text-[24px] text-slate-900 font-semibold">Body type</label>

              <div class="grid grid-cols-5 gap-4 mt-5">
                <button
                  v-for="type in bodyTypes"
                  :key="type"
                  type="button"
                  @click="bodyType = type"
                  class="cursor-pointer w-full border-2 rounded-2xl text-left transition-color overflow-hidden"
                  :class="
                    bodyType === type
                      ? 'border-primary bg-slate-50'
                      : 'border-slate-200/70 hover:border-slate-300'
                  "
                >
                  <img :src="bodtTypeImages[type]" alt="" class="h-[200px] object-cover w-full" />
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="goNextFromBodyType"
                  :disabled="!bodyType"
                  class="text-[20px] px-10 py-6 tracking-wide disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Next
                </Button>
              </div>

              <Button
                variant="ghost"
                type="button"
                class="text-slate-500 text-lg hover:bg-transparent hover:text-slate-800 underline-offset-4 hover:underline"
                @click="step = 1"
              >
                Back
              </Button>
            </div>
          </div>

          <!-- STEP 3: FACE CAPTURE -->
          <div v-else key="step-face" class="space-y-10 w-full">
            <div class="space-y-6">
              <div class="text-center space-y-2">
                <label class="text-[32px] text-slate-900 font-bold">Face recognition</label>
                <p class="text-lg text-slate-500">Position your face within the frame</p>
              </div>

              <div
                class="relative w-full aspect-video rounded-3xl overflow-hidden bg-slate-100 border-2 border-slate-200 shadow-2xl"
              >
                <!-- Video Feed -->
                <video
                  ref="videoEl"
                  autoplay
                  muted
                  playsinline
                  class="w-full h-full object-cover transform -scale-x-100"
                  @play="onPlay"
                ></video>

                <!-- Detection Canvas (Hidden but needed for logic) -->
                <canvas
                  ref="canvasEl"
                  class="absolute inset-0 w-full h-full pointer-events-none opacity-0"
                ></canvas>

                <!-- Status Overlay / Hints -->
                <div
                  v-if="!faceImage && !isLoadingModels"
                  class="absolute inset-0 flex items-center justify-center pointer-events-none"
                >
                  <!-- Frame Guide -->
                  <div
                    class="w-[400px] h-[500px] border-2 rounded-[100px] transition-all duration-500"
                    :class="{
                      'border-white/30': detectionStatus === 'SEARCHING',
                      'border-red-500/80 bg-red-500/10':
                        detectionStatus === 'MULTIPLE_FACES' ||
                        detectionStatus === 'TOO_FAR' ||
                        detectionStatus === 'TOO_CLOSE',
                      'border-green-400 shadow-[0_0_50px_rgba(74,222,128,0.3)]':
                        detectionStatus === 'PERFECT',
                    }"
                  ></div>

                  <!-- Hint Text -->
                  <div
                    class="absolute bottom-12 px-6 py-3 rounded-full bg-black/60 backdrop-blur-md text-white font-medium text-lg transition-all duration-300"
                  >
                    <span v-if="detectionStatus === 'SEARCHING'">Looking for face...</span>
                    <span v-else-if="detectionStatus === 'MULTIPLE_FACES'" class="text-red-300"
                      >Only one face allowed</span
                    >
                    <span v-else-if="detectionStatus === 'TOO_FAR'" class="text-yellow-300"
                      >Move closer</span
                    >
                    <span v-else-if="detectionStatus === 'TOO_CLOSE'" class="text-yellow-300"
                      >Move back</span
                    >
                    <span
                      v-else-if="detectionStatus === 'PERFECT'"
                      class="text-green-300 flex items-center gap-2"
                    >
                      <div class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                      Perfect position
                    </span>
                  </div>
                </div>

                <!-- Loading State -->
                <div
                  v-if="isLoadingModels"
                  class="absolute inset-0 flex items-center justify-center bg-white/90 backdrop-blur-sm z-20"
                >
                  <div class="flex flex-col items-center gap-4">
                    <div
                      class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"
                    ></div>
                    <span class="text-lg font-medium text-slate-600"
                      >Initializing AI Camera...</span
                    >
                  </div>
                </div>

                <!-- Captured Image Preview -->
                <div v-if="faceImage" class="absolute inset-0 z-30 bg-white">
                  <img :src="faceImage" class="w-full h-full object-cover" />
                  <button
                    @click="retakePhoto"
                    class="absolute top-6 right-6 p-3 rounded-full bg-black/20 backdrop-blur-md hover:bg-black/40 transition-colors text-white"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="flex justify-center pt-4">
                <Button
                  v-if="!faceImage"
                  @click="capturePhoto"
                  :disabled="isLoadingModels || detectionStatus !== 'PERFECT'"
                  class="text-[20px] px-12 py-6 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-xl shadow-primary/20"
                  :class="{ 'scale-110 shadow-primary/40': detectionStatus === 'PERFECT' }"
                >
                  <div class="flex items-center gap-3">
                    <div
                      v-if="detectionStatus === 'PERFECT'"
                      class="w-3 h-3 rounded-full bg-green-400 animate-pulse"
                    ></div>
                    {{ detectionStatus === 'PERFECT' ? 'Capture Photo' : 'Align Face to Capture' }}
                  </div>
                </Button>

                <Button
                  v-else
                  @click="handleSubmit"
                  class="text-[20px] px-16 py-6 rounded-full bg-primary hover:bg-primary/90 shadow-xl shadow-primary/20"
                >
                  Continue
                </Button>
              </div>
            </div>

            <div class="flex justify-center">
              <button
                type="button"
                class="text-sm text-slate-500 hover:text-slate-800 underline-offset-4 hover:underline"
                @click="step = 2"
              >
                Back to Body Type
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-step-enter-active,
.fade-step-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.fade-step-enter-from,
.fade-step-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
