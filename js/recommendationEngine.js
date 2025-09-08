export function showRecommendations(userData, jaccardSimilarity) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '<h4>Recomendaciones basadas en similitud:</h4>';
    
    // Para cada usuario, encontrar el más similar y recomendar items que no tenga
    userData.forEach((user, i) => {
        // Encontrar usuario más similar (excluyéndose a sí mismo)
        let maxSimilarity = 0;
        let mostSimilarUserIndex = -1;
        
        for (let j = 0; j < userData.length; j++) {
            if (i !== j && jaccardSimilarity[i][j] > maxSimilarity) {
                maxSimilarity = jaccardSimilarity[i][j];
                mostSimilarUserIndex = j;
            }
        }
        
        if (mostSimilarUserIndex !== -1 && maxSimilarity > 0.1) {
            const similarUser = userData[mostSimilarUserIndex];
            const userItems = new Set(user.titles);
            const similarUserItems = new Set(similarUser.titles);
            
            // Encontrar items en el usuario similar que el usuario actual no tiene
            const recommendations = [...similarUserItems].filter(item => !userItems.has(item));
            
            if (recommendations.length > 0) {
                const userDiv = document.createElement('div');
                userDiv.innerHTML = `
                    <p><strong>Usuario ${user.user_id}</strong> (similar a ${similarUser.user_id}, similitud: ${maxSimilarity.toFixed(2)})</p>
                    <ul>
                        ${recommendations.slice(0, 5).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                `;
                recommendationsDiv.appendChild(userDiv);
            }
        }
    });
    
    if (recommendationsDiv.children.length === 1) {
        recommendationsDiv.innerHTML += '<p>No se encontraron recomendaciones significativas.</p>';
    }
}