// 🎨 FUNCIONES DE VISUALIZACIÓN
class VisualizationManager {
    constructor() {
        this.config = {
            heatmapSize: 400,
            cellSize: 20,
            colors: {
                low: '#3182ce',
                high: '#ff6b6b',
                medium: '#feca57'
            }
        };
        
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }
    
    // 🎯 CREAR HEATMAP
    createHeatmap(userIds, similarities, containerId) {
        const container = d3.select(containerId);
        container.selectAll('*').remove();
        
        // Limitar para visualización
        const limitedUserIds = userIds.slice(0, 20);
        const size = Math.min(this.config.heatmapSize, limitedUserIds.length * this.config.cellSize);
        const cellSize = size / limitedUserIds.length;
        
        const svg = container
            .append('svg')
            .attr('width', size + 100)
            .attr('height', size + 100);
        
        // Escala de colores
        const colorScale = d3.scaleSequential()
            .domain([0, 1])
            .interpolator(d3.interpolateRdYlBu);
        
        // Crear celdas
        limitedUserIds.forEach((userId1, i) => {
            limitedUserIds.forEach((userId2, j) => {
                const similarity = similarities[userId1]?.[userId2] || 0;
                
                svg.append('rect')
                    .attr('class', 'heatmap-cell')
                    .attr('x', j * cellSize + 50)
                    .attr('y', i * cellSize + 50)
                    .attr('width', cellSize - 1)
                    .attr('height', cellSize - 1)
                    .attr('fill', colorScale(similarity))
                    .on('mouseover', (event) => {
                        this.tooltip.transition().duration(200).style('opacity', 0.9);
                        this.tooltip.html(`Usuarios: ${userId1} ↔ ${userId2}<br/>Similaridad: ${similarity.toFixed(3)}`)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 28) + 'px');
                    })
                    .on('mouseout', () => {
                        this.tooltip.transition().duration(500).style('opacity', 0);
                    });
            });
        });
        
        // Etiquetas de ejes
        svg.selectAll('.row-label')
            .data(limitedUserIds)
            .enter()
            .append('text')
            .attr('class', 'row-label')
            .attr('x', 45)
            .attr('y', (d, i) => i * cellSize + cellSize/2 + 55)
            .attr('text-anchor', 'end')
            .style('font-size', '10px')
            .text(d => d);
        
        svg.selectAll('.col-label')
            .data(limitedUserIds)
            .enter()
            .append('text')
            .attr('class', 'col-label')
            .attr('x', (d, i) => i * cellSize + cellSize/2 + 50)
            .attr('y', 45)
            .attr('text-anchor', 'middle')
            .style('font-size', '10px')
            .text(d => d);
    }
    
    // 👥 MOSTRAR USUARIOS SIMILARES
    showSimilarUsers(similarUsers, userData, containerId) {
        const container = document.getElementById(containerId);
        
        if (similarUsers.length === 0) {
            container.innerHTML = '<p class="text-muted">No se encontraron usuarios similares</p>';
            return;
        }
        
        let html = '<div class="list-group list-group-flush">';
        similarUsers.forEach((user, index) => {
            const percentage = (user.similarity * 100).toFixed(1);
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>Usuario ${user.userId}</strong>
                        <br><small class="text-muted">${userData[user.userId]?.size || 0} items</small>
                    </div>
                    <div>
                        <span class="badge bg-primary">${percentage}%</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
    
    // 📈 CREAR HISTOGRAMA
    createHistogram(similarities, containerId) {
        const container = d3.select(containerId);
        container.selectAll('*').remove();
        
        // Recopilar todas las similaridades
        const allSimilarities = [];
        Object.values(similarities).forEach(userSims => {
            allSimilarities.push(...Object.values(userSims));
        });
        
        if (allSimilarities.length === 0) return;
        
        const width = 400;
        const height = 200;
        const margin = {top: 20, right: 20, bottom: 40, left: 40};
        
        const svg = container
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Crear bins
        const bins = d3.bin()
            .domain([0, 1])
            .thresholds(20)(allSimilarities);
        
        const xScale = d3.scaleLinear()
            .domain([0, 1])
            .range([margin.left, width - margin.right]);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(bins, d => d.length)])
            .range([height - margin.bottom, margin.top]);
        
        // Crear barras
        svg.selectAll('rect')
            .data(bins)
            .enter()
            .append('rect')
            .attr('x', d => xScale(d.x0) + 1)
            .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 2))
            .attr('y', d => yScale(d.length))
            .attr('height', d => yScale(0) - yScale(d.length))
            .attr('fill', this.config.colors.medium)
            .attr('opacity', 0.7);
        
        // Ejes
        svg.append('g')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.format('.1f')));
        
        svg.append('g')
            .attr('transform', `translate(${margin.left},0)`)
            .call(d3.axisLeft(yScale));
    }
    
    // 👤 MOSTRAR PERFIL DE USUARIO
    showUserProfile(userId, userItems, containerId) {
        const container = document.getElementById(containerId);
        
        if (!userItems || userItems.size === 0) {
            container.innerHTML = '<p class="text-muted">Usuario sin items</p>';
            return;
        }
        
        let html = `
            <div class="mb-3">
                <h6><i class="fas fa-list"></i> Items del Usuario ${userId} (${userItems.size})</h6>
                <div class="mt-2">
        `;
        
        [...userItems].slice(0, 10).forEach(item => {
            html += `<span class="user-item">${item}</span>`;
        });
        
        if (userItems.size > 10) {
            html += `<span class="user-item bg-secondary text-white">+${userItems.size - 10} más...</span>`;
        }
        
        html += '</div></div>';
        
        container.innerHTML = html;
    }
    
    // 📊 ACTUALIZAR ESTADÍSTICAS
    updateStats(stats) {
        if (!stats) return;
        
        document.getElementById('totalUsers').textContent = stats.totalUsers;
        document.getElementById('totalItems').textContent = stats.totalItems;
        document.getElementById('avgSimilarity').textContent = stats.avgSimilarity.toFixed(3);
        document.getElementById('maxSimilarity').textContent = stats.maxSimilarity.toFixed(3);
    }
    
    // 👤 ACTUALIZAR SELECTOR DE USUARIOS
    updateUserSelect(userData, selectId) {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Seleccionar usuario...</option>';
        
        Object.keys(userData).sort((a, b) => parseInt(a) - parseInt(b)).forEach(userId => {
            const option = document.createElement('option');
            option.value = userId;
            option.textContent = `Usuario ${userId} (${userData[userId].size} items)`;
            select.appendChild(option);
        });
        
        select.disabled = false;
    }
    
    // 🔄 MOSTRAR/OCULTAR PROGRESO
    showProgress(show) {
        document.getElementById('progressContainer').style.display = show ? 'block' : 'none';
    }
    
    // 👀 MOSTRAR/OCULTAR CONTENEDORES
    toggleContainers(show) {
        document.getElementById('statsContainer').style.display = show ? 'block' : 'none';
        document.getElementById('visualizationsContainer').style.display = show ? 'block' : 'none';
    }
}