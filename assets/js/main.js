// 🚀 LÓGICA PRINCIPAL Y EVENT LISTENERS

// 🎯 VARIABLES GLOBALES
let analyzer = new JaccardAnalyzer();
let dataHandler = new DataHandler(analyzer);
let visualizationManager = new VisualizationManager();

let userData = {};
let similarities = {};
let currentUser = null;

// 📋 INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Visualizador de Similaridad Jaccard iniciado');
    console.log('📝 Cargar un archivo CSV para comenzar');
    
    setupEventListeners();
});

// 🎛️ CONFIGURAR EVENT LISTENERS
function setupEventListeners() {
    // Cargar archivo CSV
    document.getElementById('csvFile').addEventListener('change', handleFileUpload);
    
    // Seleccionar usuario
    document.getElementById('userSelect').addEventListener('change', handleUserSelect);
    
    // Cambiar similaridad mínima
    document.getElementById('minSimilarity').addEventListener('input', handleMinSimilarityChange);
    
    // Cargar datos de ejemplo
    document.getElementById('loadSampleData').addEventListener('click', loadSampleData);
}

// 📁 MANEJAR CARGA DE ARCHIVO
function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    visualizationManager.showProgress(true);
    
    dataHandler.loadCSV(
        file,
        function(results) {
            console.log('📊 Datos cargados:', results.data.length, 'filas');
            
            // Validar CSV
            const validation = dataHandler.validateCSV(results.data);
            if (!validation.valid) {
                alert(validation.error);
                visualizationManager.showProgress(false);
                return;
            }
            
            processData(results.data);
        },
        function(error) {
            console.error('❌ Error al cargar CSV:', error);
            alert('Error al cargar el archivo CSV');
            visualizationManager.showProgress(false);
        }
    );
}

// 🔄 PROCESAR DATOS
function processData(csvData) {
    const minSim = parseFloat(document.getElementById('minSimilarity').value);
    
    const result = dataHandler.processData(csvData, minSim);
    
    if (result.success) {
        userData = result.userData;
        similarities = result.similarities;
        
        // Actualizar UI
        visualizationManager.updateUserSelect(userData, 'userSelect');
        visualizationManager.updateStats(result.stats);
        
        visualizationManager.showProgress(false);
        visualizationManager.toggleContainers(true);
        
        console.log('✅ Procesamiento completado');
    } else {
        alert('Error al procesar los datos: ' + result.error);
        visualizationManager.showProgress(false);
    }
}

// 👤 MANEJAR SELECCIÓN DE USUARIO
function handleUserSelect(e) {
    const userId = parseInt(e.target.value);
    if (userId) {
        currentUser = userId;
        
        const userIds = Object.keys(similarities).map(d => parseInt(d)).sort((a, b) => a - b);
        
        // Actualizar visualizaciones
        visualizationManager.createHeatmap(userIds, similarities, '#heatmap');
        visualizationManager.showSimilarUsers(
            analyzer.getSimilarUsers(userId, 10), 
            userData, 
            'similarUsers'
        );
        visualizationManager.showUserProfile(userId, userData[userId], 'userProfile');
        visualizationManager.createHistogram(similarities, '#histogram');
    }
}

// 📏 MANEJAR CAMBIO DE SIMILARIDAD MÍNIMA
function handleMinSimilarityChange(e) {
    const value = e.target.value;
    document.getElementById('minSimilarityValue').textContent = value;
    
    // Recalcular si hay datos
    if (Object.keys(userData).length > 0) {
        visualizationManager.showProgress(true);
        
        setTimeout(() => {
            const minSim = parseFloat(value);
            similarities = analyzer.calculateAllSimilarities(minSim);
            
            visualizationManager.updateStats(analyzer.getStats());
            
            if (currentUser) {
                const userIds = Object.keys(similarities).map(d => parseInt(d)).sort((a, b) => a - b);
                visualizationManager.createHeatmap(userIds, similarities, '#heatmap');
                visualizationManager.showSimilarUsers(
                    analyzer.getSimilarUsers(currentUser, 10), 
                    userData, 
                    'similarUsers'
                );
                visualizationManager.createHistogram(similarities, '#histogram');
            }
            
            visualizationManager.showProgress(false);
        }, 100);
    }
}

// 🧪 CARGAR DATOS DE EJEMPLO
function loadSampleData() {
    visualizationManager.showProgress(true);
    
    // Simular carga asíncrona
    setTimeout(() => {
        const sampleData = dataHandler.generateSampleData();
        processData(sampleData);
        
        // Seleccionar primer usuario automáticamente
        setTimeout(() => {
            document.getElementById('userSelect').value = Object.keys(userData)[0];
            document.getElementById('userSelect').dispatchEvent(new Event('change'));
        }, 500);
        
    }, 800);
}