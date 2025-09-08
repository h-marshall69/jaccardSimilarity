// 📁 MANEJO DE DATOS Y CSV
class DataHandler {
    constructor(analyzer) {
        this.analyzer = analyzer;
    }
    
    // Cargar datos desde un archivo CSV
    loadCSV(file, onComplete, onError) {
        Papa.parse(file, {
            header: true,
            complete: onComplete,
            error: onError
        });
    }
    
    // Procesar datos CSV
    processData(csvData, minSimilarity = 0.1) {
        try {
            // Preparar datos
            const userData = this.analyzer.prepareData(csvData);
            
            // Calcular similaridades
            const similarities = this.analyzer.calculateAllSimilarities(minSimilarity);
            
            return {
                success: true,
                userData: userData,
                similarities: similarities,
                stats: this.analyzer.getStats()
            };
        } catch (error) {
            console.error('❌ Error en procesamiento:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    // Generar datos de ejemplo para pruebas
    generateSampleData() {
        return [
            {user_id: "1", original_title: "Toy Story,Finding Nemo,The Incredibles"},
            {user_id: "2", original_title: "Toy Story,Toy Story 2,Monsters Inc"},
            {user_id: "3", original_title: "Finding Nemo,The Incredibles,Ratatouille"},
            {user_id: "4", original_title: "Toy Story,Monsters Inc,Finding Nemo"},
            {user_id: "5", original_title: "Ratatouille,Coco,Inside Out"},
            {user_id: "6", original_title: "Toy Story,The Incredibles,Up"},
            {user_id: "7", original_title: "Finding Nemo,Monsters Inc,Cars"},
            {user_id: "8", original_title: "The Incredibles,Ratatouille,WALL-E"},
            {user_id: "9", original_title: "Toy Story 2,Finding Nemo,Monsters Inc"},
            {user_id: "10", original_title: "Coco,Inside Out,Soul"}
        ];
    }
    
    // Validar estructura del CSV
    validateCSV(data) {
        if (!data || data.length === 0) {
            return { valid: false, error: "El archivo CSV está vacío" };
        }
        
        const firstRow = data[0];
        if (!firstRow.hasOwnProperty('user_id') || !firstRow.hasOwnProperty('original_title')) {
            return { 
                valid: false, 
                error: "El CSV debe contener las columnas: user_id, original_title" 
            };
        }
        
        return { valid: true };
    }
}