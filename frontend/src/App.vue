<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const file = ref<File | null>(null);
const question = ref('');
const answer = ref('');
const paperId = ref<string | null>(null);
const isLoading = ref(false);
const errorMessage = ref('');

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    file.value = target.files[0];
  }
};

const uploadFile = async () => {
  if (!file.value) {
    errorMessage.value = 'Please select a file first.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  const formData = new FormData();
  formData.append('file', file.value);

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/papers', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('API Response:', response.data);
    paperId.value = response.data.id;
    answer.value = `File "${file.value.name}" uploaded and parsed successfully. You can now ask questions about it.`;
  } catch (error) {
    errorMessage.value = 'Error uploading file. Please try again.';
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const askQuestion = async () => {
  if (!paperId.value || !question.value) {
    errorMessage.value = 'Please upload a paper and enter a question.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/v1/papers/${paperId.value}/ask`, {
      question: question.value,
    });
    answer.value = response.data.answer;
  } catch (error) {
    errorMessage.value = 'Error asking question. Please try again.';
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div id="app">
    <h1>Paper Pilot</h1>
    <p>Your AI-powered paper analysis assistant</p>

    <div class="card">
      <h2>1. Upload Paper</h2>
      <input type="file" @change="handleFileChange" accept=".pdf" />
      <button @click="uploadFile" :disabled="isLoading || !file">
        {{ isLoading ? 'Uploading...' : 'Upload and Parse' }}
      </button>
    </div>

    <div v-if="paperId" class="card">
      <h2>2. Ask a Question</h2>
      <textarea v-model="question" placeholder="e.g., What is the main contribution of this paper?"></textarea>
      <button @click="askQuestion" :disabled="isLoading || !question">
        {{ isLoading ? 'Thinking...' : 'Ask' }}
      </button>
    </div>

    <div v-if="answer || errorMessage" class="card result">
      <h2>Answer</h2>
      <p v-if="answer">{{ answer }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin: 20px auto;
  max-width: 600px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
  font-size: 2.5em;
}

h2 {
  color: #42b883;
}

input[type="file"] {
  margin-bottom: 10px;
}

button {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #36a374;
}

textarea {
  width: 95%;
  height: 80px;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
  margin-bottom: 10px;
  font-size: 1em;
}

.result {
  text-align: left;
  white-space: pre-wrap; /* This will respect newlines in the answer */
}

.error {
  color: #e74c3c;
}
</style>
