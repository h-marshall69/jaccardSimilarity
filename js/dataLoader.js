export function loadCSVData(csvFileInput) {
    const file = csvFileInput.files[0];
    if (!file) {
        alert('Por favor, selecciona un archivo CSV');
        return;
    }
    
    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            userData = results.data.map(row => {
                const titles = row.original_title 
                    ? row.original_title.replace(/NaN/g, '').split(',').map(t => t.trim()).filter(t => t)
                    : [];
                return {
                    user_id: row.user_id,
                    titles: titles,
                    titles_count: titles.length // Agregar contador
                };
            });
            
            userIds = userData.map(user => user.user_id);
            
            alert(`Datos cargados: ${userData.length} usuarios`);
            
            // IMPRIMIR DATOS EN CONSOLA
            console.log('=== DATOS CARGADOS DEL CSV ===');
            console.log(`Total de usuarios: ${userData.length}`);
            console.log('----------------------------------------');
            
            // Mostrar como tabla
            console.table(userData.map(user => ({
                'User ID': user.user_id,
                'Cantidad de títulos': user.titles_count,
                'Títulos': user.titles.join(', ')
            })));
            
            // Mostrar estadísticas
            console.log('\n=== ESTADÍSTICAS ===');
            console.log(`IDs de usuarios: [${userIds.join(', ')}]`);
            console.log(`Usuario con más títulos: ${Math.max(...userData.map(u => u.titles.length))}`);
            console.log(`Usuario con menos títulos: ${Math.min(...userData.map(u => u.titles.length))}`);
            
        },
        error: function(error) {
            console.error('Error al cargar CSV:', error);
            alert('Error al cargar el archivo CSV');
        }
    });
}