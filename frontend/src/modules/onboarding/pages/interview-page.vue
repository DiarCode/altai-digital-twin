<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import { ChevronLeft, ChevronRight, Mic, Pause, Play, RotateCw } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

type QuestionType = 'LICKERT' | 'AUDIO'

interface QuestionDTO {
  id: number
  question: string
  type: QuestionType
}

interface QuestionAnswerRequest {
  audio?: Blob
  answer: string
}

const router = useRouter()

// Mock questions
const questions: QuestionDTO[] = [
  {
    id: 1,
    question: 'How satisfied are you with your current work-life balance?',
    type: 'LICKERT',
  },
  { id: 2, question: 'Tell us about your proudest professional achievement', type: 'AUDIO' },
  {
    id: 3,
    question: 'How comfortable are you with adapting to new technologies?',
    type: 'LICKERT',
  },
  {
    id: 4,
    question: 'Describe a challenging situation you faced and how you overcame it',
    type: 'AUDIO',
  },
  { id: 5, question: 'How would you rate your communication skills?', type: 'LICKERT' },
]

const currentQuestionIndex = ref(0)
const answers = ref<Record<number, QuestionAnswerRequest>>({})

// Audio recording state
const isRecording = ref(false)
const recordedAudio = ref<Blob | null>(null)
const audioUrl = ref<string | null>(null)
const recordingTime = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const recordingInterval = ref<number | null>(null)

// Playback state (custom player)
const isPlaying = ref(false)
const playbackTime = ref(0)
const playbackDuration = ref(0)
const playbackProgress = computed(() =>
  playbackDuration.value ? (playbackTime.value / playbackDuration.value) * 100 : 0,
)

let audioElement: HTMLAudioElement | null = null

const waveformBars = Array.from({ length: 32 }, (_, i) => i)

const currentQuestion = computed(() => questions[currentQuestionIndex.value])
const progress = computed(() => ((currentQuestionIndex.value + 1) / questions.length) * 100)

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const selectLickertAnswer = (value: number) => {
  answers.value[currentQuestion.value.id] = { answer: value.toString() }
}

const setupAudioElement = (url: string) => {
  if (audioElement) {
    audioElement.pause()
    audioElement.src = ''
    audioElement = null
  }

  audioElement = new Audio(url)

  audioElement.addEventListener('timeupdate', () => {
    playbackTime.value = Math.floor(audioElement?.currentTime || 0)
  })

  audioElement.addEventListener('loadedmetadata', () => {
    playbackDuration.value = Math.floor(audioElement?.duration || 0)
  })

  audioElement.addEventListener('ended', () => {
    isPlaying.value = false
    playbackTime.value = 0
  })
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    const chunks: BlobPart[] = []

    mediaRecorder.value.ondataavailable = (e) => {
      chunks.push(e.data)
    }

    mediaRecorder.value.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' })
      recordedAudio.value = blob

      const url = URL.createObjectURL(blob)
      audioUrl.value = url
      setupAudioElement(url)

      answers.value[currentQuestion.value.id] = { audio: blob, answer: '' }

      stream.getTracks().forEach((track) => track.stop())
    }

    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0

    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
      recordingInterval.value = null
    }

    recordingInterval.value = window.setInterval(() => {
      recordingTime.value++
    }, 1000)
  } catch (error) {
    console.error('Error accessing microphone:', error)
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
      recordingInterval.value = null
    }
  }
}

const toggleRecord = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    reRecord() // clear previous audio if any
    startRecording()
  }
}

const togglePlay = () => {
  if (!audioElement || !recordedAudio.value) return

  if (isPlaying.value) {
    audioElement.pause()
    isPlaying.value = false
  } else {
    audioElement.currentTime = playbackTime.value
    audioElement
      .play()
      .then(() => {
        isPlaying.value = true
      })
      .catch((err) => console.error('Error playing audio', err))
  }
}

const reRecord = () => {
  if (audioElement) {
    audioElement.pause()
    audioElement.src = ''
    audioElement = null
  }
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }

  isPlaying.value = false
  playbackTime.value = 0
  playbackDuration.value = 0

  recordedAudio.value = null
  audioUrl.value = null
  recordingTime.value = 0

  delete answers.value[currentQuestion.value.id]
}

const resetAudioState = () => {
  if (isRecording.value) {
    stopRecording()
  }

  if (audioElement) {
    audioElement.pause()
    audioElement.src = ''
    audioElement = null
  }

  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
    audioUrl.value = null
  }

  isRecording.value = false
  isPlaying.value = false
  recordingTime.value = 0
  playbackTime.value = 0
  playbackDuration.value = 0
  recordedAudio.value = null
}

const goNext = () => {
  if (currentQuestionIndex.value < questions.length - 1) {
    currentQuestionIndex.value++
    resetAudioState()
  }
}

const goBack = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    resetAudioState()
  }
}

const handleSubmit = () => {
  console.log('Submitting answers:', answers.value)
  router.push('/home')
}

const canProceed = computed(() => {
  const answer = answers.value[currentQuestion.value.id]
  if (currentQuestion.value.type === 'LICKERT') {
    return answer && answer.answer
  }
  return answer && answer.audio
})
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

    <!-- Progress -->
    <div class="absolute top-8 right-8 z-10 flex items-center gap-4">
      <span class="text-[20px] text-slate-400 font-medium"
        >{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span
      >
      <div class="w-48 h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          class="h-full bg-primary transition-all duration-300"
          :style="{ width: progress + '%' }"
        ></div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex items-center justify-center px-8 relative z-10">
      <div class="w-full max-w-4xl">
        <Transition name="fade-step" mode="out-in">
          <div :key="currentQuestion.id" class="space-y-12">
            <!-- Question -->
            <div class="space-y-4">
              <div class="text-[20px] text-slate-400 font-medium">
                Question {{ currentQuestionIndex + 1 }}
              </div>
              <h1 class="text-[36px] text-black font-bold leading-tight">
                {{ currentQuestion.question }}
              </h1>
            </div>

            <!-- LICKERT Scale -->
            <div v-if="currentQuestion.type === 'LICKERT'" class="space-y-8">
              <div class="flex justify-between items-center gap-4">
                <button
                  v-for="value in [1, 2, 3, 4, 5]"
                  :key="value"
                  @click="selectLickertAnswer(value)"
                  :class="[
                    'flex-1 aspect-square rounded-4xl border-2 transition-all duration-200',
                    'flex flex-col items-center justify-center gap-2',
                    answers[currentQuestion.id]?.answer === value.toString()
                      ? 'border-primary bg-primary text-white! scale-105'
                      : 'border-slate-400/20 hover:border-slate-400 hover:bg-slate-50/20',
                  ]"
                >
                  <span class="text-[32px] font-bold">{{ value }}</span>
                </button>
              </div>
              <div class="flex justify-between text-[16px] text-slate-500 px-2">
                <span>Strongly Disagree</span>
                <span>Strongly Agree</span>
              </div>
            </div>

            <!-- AUDIO Recording (minimal, futuristic) -->
            <div v-else class="flex items-center gap-6">
              <!-- Record icon + status/time -->
              <div class="flex items-center gap-6">
                <button
                  type="button"
                  class="relative flex size-24 items-center justify-center rounded-full border border-slate-200 bg-primary shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                  @click="toggleRecord"
                >
                  <Mic v-if="!isRecording" class="relative z-10 size-8 text-white" />
                  <Pause v-else class="relative z-10 size-8 text-red-500" />
                </button>

                <span class="font-mono text-3xl text-slate-900">
                  {{ formatTime(isRecording ? recordingTime : playbackTime || recordingTime) }}
                </span>
              </div>

              <!-- Playback controls -->
              <div v-if="recordedAudio" class="flex items-center gap-3">
                <button
                  type="button"
                  class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-900 shadow-sm transition hover:shadow-md"
                  @click="togglePlay"
                >
                  <Play v-if="!isPlaying" class="h-4 w-4" />
                  <Pause v-else class="h-4 w-4" />
                </button>

                <button
                  type="button"
                  class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-900 shadow-sm transition hover:shadow-md"
                  @click="reRecord"
                >
                  <RotateCw class="h-4 w-4" />
                </button>
              </div>
            </div>

            <!-- Navigation -->
            <div class="flex items-center justify-between pt-8">
              <Button
                v-if="currentQuestionIndex > 0"
                @click="goBack"
                variant="outline"
                class="text-[18px] px-8! py-8 rounded-xl border-2 border-none! outline-none!"
              >
                <ChevronLeft class="size-5" /> Back
              </Button>
              <div v-else></div>

              <Button
                v-if="currentQuestionIndex < questions.length - 1"
                @click="goNext"
                :disabled="!canProceed"
                class="text-[20px] px-8! py-8 rounded-xl bg-black hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next Question <ChevronRight class="size-5" />
              </Button>
              <Button
                v-else
                @click="handleSubmit"
                :disabled="!canProceed"
                class="text-[20px] px-12 py-8 rounded-xl bg-primary hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Submit Interview
              </Button>
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
    opacity 0.3s ease,
    transform 0.3s ease;
}
.fade-step-enter-from,
.fade-step-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* Waveform animations */
@keyframes waveBar {
  0%,
  100% {
    transform: scaleY(0.4);
  }
  50% {
    transform: scaleY(1);
  }
}

@keyframes waveBarSoft {
  0%,
  100% {
    transform: scaleY(0.7);
  }
  50% {
    transform: scaleY(1);
  }
}

.animate-wave-bar {
  animation: waveBar 1s ease-in-out infinite;
}

.animate-wave-bar-soft {
  animation: waveBarSoft 1.4s ease-in-out infinite;
}
</style>
