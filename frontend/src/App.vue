<template>
  <div class="app-container">
    <header class="app-header">
      <h1>MRI/CT 医学图像分割系统</h1>
      <p>上传CT/MRI图像，实时查看分割结果</p>
    </header>
    
    <main class="app-main">
      <div class="input-section">
        <h2>图像输入</h2>
        <input @change="handleFileUpload" type="file" accept=".nii,.nii.gz" />
      </div>
      
      <div class="preview-section">
        <div class="input-preview">
          <h2>原始图像 (3D)</h2>
          <canvas ref="inputCanvas"></canvas>
        </div>
        
        <div class="loading-section" v-if="isLoading">
          <div class="loading-circle"></div>
          <p>正在分割中... {{ progress }}%</p>
        </div>
        
        <div class="result-preview" v-else>
          <h2>分割结果</h2>
          <canvas ref="resultCanvas"></canvas>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const inputCanvas = ref(null)
    const resultCanvas = ref(null)
    const isLoading = ref(false)
    const progress = ref(0)
    let inputScene = null
    let inputCamera = null
    let inputRenderer = null
    let resultScene = null
    let resultCamera = null
    let resultRenderer = null

    const handleFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      isLoading.value = true
      progress.value = 0

      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await axios.post('/api/segment', formData, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
          }
        })

        if (response.data.success) {
          load3DModel(response.data.inputData, 'input')
          load3DModel(response.data.resultData, 'result')
        }
      } catch (error) {
        console.error('分割失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    const initThreeJS = (canvasRef, type) => {
      const canvas = canvasRef.value
      if (!canvas) return

      const scene = new THREE.Scene()
      scene.background = new THREE.Color(0x1a1a2e)

      const camera = new THREE.PerspectiveCamera(
        75,
        canvas.clientWidth / canvas.clientHeight,
        0.1,
        1000
      )
      camera.position.z = 5

      const renderer = new THREE.WebGLRenderer({ canvas, alpha: true })
      renderer.setSize(canvas.clientWidth, canvas.clientHeight)
      renderer.setPixelRatio(window.devicePixelRatio)

      const controls = new OrbitControls(camera, renderer.domElement)
      controls.enableDamping = true
      controls.dampingFactor = 0.05

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
      scene.add(ambientLight)

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
      directionalLight.position.set(5, 5, 5)
      scene.add(directionalLight)

      return { scene, camera, renderer, controls }
    }

    const load3DModel = (data, type) => {
      const { scene, camera, renderer, controls } = type === 'input' 
        ? initThreeJS(inputCanvas, 'input') 
        : initThreeJS(resultCanvas, 'result')

      if (!scene) return

      const geometry = new THREE.SphereGeometry(1, 32, 32)
      const material = new THREE.MeshPhongMaterial({
        color: type === 'input' ? 0x00ff88 : 0xff0088,
        transparent: true,
        opacity: 0.8
      })
      const sphere = new THREE.Mesh(geometry, material)
      scene.add(sphere)

      const animate = () => {
        requestAnimationFrame(animate)
        controls.update()
        renderer.render(scene, camera)
      }
      animate()
    }

    onMounted(() => {
      // 初始化ThreeJS场景
      initThreeJS(inputCanvas, 'input')
      initThreeJS(resultCanvas, 'result')
    })

    return {
      inputCanvas,
      resultCanvas,
      isLoading,
      progress,
      handleFileUpload
    }
  }
}
</script>

<style scoped>
.app-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
}

.app-header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.input-section h2 {
  margin-bottom: 15px;
  color: #333;
}

.input-section input[type="file"] {
  padding: 10px;
  border: 2px dashed #667eea;
  border-radius: 5px;
  background: #f0f4ff;
  cursor: pointer;
}

.preview-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.input-preview, .result-preview, .loading-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.input-preview h2, .result-preview h2 {
  margin-bottom: 15px;
  color: #333;
}

.input-preview canvas, .result-preview canvas {
  width: 100%;
  height: 400px;
  border-radius: 5px;
  background: #1a1a2e;
}

.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.loading-circle {
  width: 80px;
  height: 80px;
  border: 8px solid #f3f3f3;
  border-top: 8px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-section p {
  font-size: 1.2rem;
  color: #666;
}
</style>