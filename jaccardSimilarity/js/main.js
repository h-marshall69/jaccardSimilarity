import { loadCSVData, userData, userIds } from './dataLoader.js';
import { calculateJaccardSimilarity, jaccardSimilarity } from './jaccardCalculator.js';
import { renderGraph } from './graphRenderer.js';
import { renderDendrogram } from './dendrogramRenderer.js';
import { showRecommendations } from './recommendationEngine.js';

// Variables globales
let similarityThresholdValue = 0.3;

// Elementos del DOM
const csvFileInput = document.getElementById('csvFile');
const loadDataBtn = document.getElementById('loadData');
const calculateSimilarityBtn = document.getElementById('calculateSimilarity');
const showGraphBtn = document.getElementById('showGraph');
const showDendrogramBtn = document.getElementById('showDendrogram');
const showRecommendationsBtn = document.getElementById('showRecommendations');
const similarityThreshold = document.getElementById('similarityThreshold');
const thresholdValue = document.getElementById('thresholdValue');

// Event listeners
loadDataBtn.addEventListener('click', () => loadCSVData(csvFileInput));
calculateSimilarityBtn.addEventListener('click', handleCalculateSimilarity);
showGraphBtn.addEventListener('click', handleShowGraph);
showDendrogramBtn.addEventListener('click', handleShowDendrogram);
showRecommendationsBtn.addEventListener('click', handleShowRecommendations);
similarityThreshold.addEventListener('input', updateThreshold);

// Actualizar valor del umbral
function updateThreshold() {
    similarityThresholdValue = parseFloat(similarityThreshold.value);
    thresholdValue.textContent = similarityThresholdValue;
}

// Manejadores de eventos
function handleCalculateSimilarity() {
    if (userData.length === 0) {
        alert('Primero carga los datos');
        return;
    }
    
    calculateJaccardSimilarity(userData);
    alert('Similitud de Jaccard calculada');
}

function handleShowGraph() {
    if (jaccardSimilarity.length === 0) {
        alert('Primero calcula la similitud');
        return;
    }
    
    renderGraph(userData, userIds, jaccardSimilarity, similarityThresholdValue);
}

function handleShowDendrogram() {
    if (jaccardSimilarity.length === 0) {
        alert('Primero calcula la similitud');
        return;
    }
    
    renderDendrogram(jaccardSimilarity, userIds);
}

function handleShowRecommendations() {
    if (jaccardSimilarity.length === 0) {
        alert('Primero calcula la similitud');
        return;
    }
    
    showRecommendations(userData, jaccardSimilarity);
}

// Inicialización
updateThreshold();