        // 🎯 VARIABLES GLOBALES
        let userData = {};
        let similarities = {};
        let currentUser = null;
        
        // 🎨 COLORES Y CONFIGURACIÓN
        const config = {
            heatmapSize: 400,
            cellSize: 20,
            colors: {
                low: '#3182ce',
                high: '#ff6b6b',
                medium: '#feca57'
            }
        };
        
        // 📊 CLASE PRINCIPAL PARA JACCARD
        class JaccardAnalyzer {
            constructor() {
                this.users = {};
                this.similarities = {};
            }
            
            // Calcular similaridad de Jaccard entre dos conjuntos
            jaccardSimilarity(set1, set2) {
                if (set1.size === 0 && set2.size === 0) return 0;
                
                const intersection = new Set([...set1].filter(x => set2.has(x)));
                const union = new Set([...set1, ...set2]);
                
                return union.size === 0 ? 0 : intersection.size / union.size;
            }
            
            // Preparar datos del CSV
            prepareData(csvData) {
                csvData.forEach(row => {
                    const userId = parseInt(row.user_id);
                    const items = row.original_title;
                    
                    if (items && items !== 'NaN') {
                        const itemList = items.split(',').map(item => item.trim()).filter(item => item && item !== 'NaN');
                        this.users[userId] = new Set(itemList);
                    }
                });
                
                return this.users;
            }
            
            // Calcular todas las similaridades
            calculateAllSimilarities(minSimilarity = 0) {
                const userIds = Object.keys(this.users).map(id => parseInt(id));
                const similarities = {};
                
                userIds.forEach(userId => {
                    similarities[userId] = {};
                });
                
                for (let i = 0; i < userIds.length; i++) {
                    for (let j = i + 1; j < userIds.length; j++) {
                        const user1 = userIds[i];
                        const user2 = userIds[j];
                        
                        const similarity = this.jaccardSimilarity(
                            this.users[user1], 
                            this.users[user2]
                        );
                        
                        if (similarity >= minSimilarity) {
                            similarities[user1][user2] = similarity;
                            similarities[user2][user1] = similarity;
                        }
                    }
                }
                
                this.similarities = similarities;
                return similarities;
            }
            
            // Obtener usuarios más similares
            getSimilarUsers(userId, topK = 10) {
                const userSimilarities = this.similarities[userId] || {};
                
                return Object.entries(userSimilarities)
                    .map(([otherUser, similarity]) => ({
                        userId: parseInt(otherUser),
                        similarity: similarity
                    }))
                    .sort((a, b) => b.similarity - a.similarity)
                    .slice(0, topK);
            }
            
            // Estadísticas generales
            getStats() {
                const allSimilarities = [];
                Object.values(this.similarities).forEach(userSims => {
                    allSimilarities.push(...Object.values(userSims));
                });
                
                if (allSimilarities.length === 0) return null;
                
                return {
                    totalUsers: Object.keys(this.users).length,
                    totalItems: new Set(Object.values(this.users).flatMap(userSet => [...userSet])).size,
                    avgSimilarity: _.mean(allSimilarities),
                    maxSimilarity: _.max(allSimilarities),
                    minSimilarity: _.min(allSimilarities),
                    medianSimilarity: _.median(allSimilarities)
                };
            }
        }
        
        // 🎯 INSTANCIA PRINCIPAL
        const analyzer = new JaccardAnalyzer();
        
        // 📁 MANEJO DE ARCHIVOS CSV
        document.getElementById('csvFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            showProgress(true);
            
            Papa.parse(file, {
                header: true,
                complete: function(results) {
                    console.log('📊 Datos cargados:', results.data.length, 'filas');
                    processData(results.data);
                },
                error: function(error) {
                    console.error('❌ Error al cargar CSV:', error);
                    alert('Error al cargar el archivo CSV');
                    showProgress(false);
                }
            });
        });
        
        // 🔄 PROCESAMIENTO DE DATOS
        function processData(csvData) {
            try {
                // Preparar datos
                userData = analyzer.prepareData(csvData);
                
                // Calcular similaridades
                const minSim = parseFloat(document.getElementById('minSimilarity').value);
                similarities = analyzer.calculateAllSimilarities(minSim);
                
                // Actualizar UI
                updateUserSelect();
                updateStats();
                
                showProgress(false);
                document.getElementById('statsContainer').style.display = 'block';
                document.getElementById('visualizationsContainer').style.display = 'block';
                
                console.log('✅ Procesamiento completado');
                
            } catch (error) {
                console.error('❌ Error en procesamiento:', error);
                alert('Error al procesar los datos');
                showProgress(false);
            }
        }
        
        // 📊 ACTUALIZAR ESTADÍSTICAS
        function updateStats() {
            const stats = analyzer.getStats();
            if (!stats) return;
            
            document.getElementById('totalUsers').textContent = stats.totalUsers;
            document.getElementById('totalItems').textContent = stats.totalItems;
            document.getElementById('avgSimilarity').textContent = stats.avgSimilarity.toFixed(3);
            document.getElementById('maxSimilarity').textContent = stats.maxSimilarity.toFixed(3);
        }
        
        // 👤 ACTUALIZAR SELECTOR DE USUARIOS
        function updateUserSelect() {
            const select = document.getElementById('userSelect');
            select.innerHTML = '<option value="">Seleccionar usuario...</option>';
            
            Object.keys(userData).sort((a, b) => parseInt(a) - parseInt(b)).forEach(userId => {
                const option = document.createElement('option');
                option.value = userId;
                option.textContent = `Usuario ${userId} (${userData[userId].size} items)`;
                select.appendChild(option);
            });
            
            select.disabled = false;
        }
        
        // 🎨 CREAR HEATMAP
        function createHeatmap(targetUser) {
            const container = d3.select('#heatmap');
            container.selectAll('*').remove();
            
            const userIds = Object.keys(similarities).map(d => parseInt(d)).sort((a, b) => a - b).slice(0, 20); // Límite para visualización
            const size = Math.min(config.heatmapSize, userIds.length * config.cellSize);
            const cellSize = size / userIds.length;
            
            const svg = container
                .append('svg')
                .attr('width', size + 100)
                .attr('height', size + 100);
            
            // Escala de colores
            const colorScale = d3.scaleSequential()
                .domain([0, 1])
                .interpolator(d3.interpolateRdYlBu);
            
            // Crear tooltip
            const tooltip = d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
            
            // Crear celdas
            userIds.forEach((userId1, i) => {
                userIds.forEach((userId2, j) => {
                    const similarity = similarities[userId1]?.[userId2] || 0;
                    
                    svg.append('rect')
                        .attr('class', 'heatmap-cell')
                        .attr('x', j * cellSize + 50)
                        .attr('y', i * cellSize + 50)
                        .attr('width', cellSize - 1)
                        .attr('height', cellSize - 1)
                        .attr('fill', colorScale(similarity))
                        .on('mouseover', function(event) {
                            tooltip.transition().duration(200).style('opacity', 0.9);
                            tooltip.html(`Usuarios: ${userId1} ↔ ${userId2}<br/>Similaridad: ${similarity.toFixed(3)}`)
                                .style('left', (event.pageX + 10) + 'px')
                                .style('top', (event.pageY - 28) + 'px');
                        })
                        .on('mouseout', function() {
                            tooltip.transition().duration(500).style('opacity', 0);
                        });
                });
            });
            
            // Etiquetas de ejes
            svg.selectAll('.row-label')
                .data(userIds)
                .enter()
                .append('text')
                .attr('class', 'row-label')
                .attr('x', 45)
                .attr('y', (d, i) => i * cellSize + cellSize/2 + 55)
                .attr('text-anchor', 'end')
                .style('font-size', '10px')
                .text(d => d);
            
            svg.selectAll('.col-label')
                .data(userIds)
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
        function showSimilarUsers(userId) {
            const similarUsers = analyzer.getSimilarUsers(userId, 10);
            const container = document.getElementById('similarUsers');
            
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
        function createHistogram() {
            const container = d3.select('#histogram');
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
                .attr('fill', config.colors.medium)
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
        function showUserProfile(userId) {
            const userItems = userData[userId];
            const container = document.getElementById('userProfile');
            
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
        
        // 🎛️ EVENT LISTENERS
        document.getElementById('userSelect').addEventListener('change', function(e) {
            const userId = parseInt(e.target.value);
            if (userId) {
                currentUser = userId;
                createHeatmap(userId);
                showSimilarUsers(userId);
                showUserProfile(userId);
                createHistogram();
            }
        });
        
        document.getElementById('minSimilarity').addEventListener('input', function(e) {
            const value = e.target.value;
            document.getElementById('minSimilarityValue').textContent = value;
            
            // Recalcular si hay datos
            if (Object.keys(userData).length > 0) {
                showProgress(true);
                setTimeout(() => {
                    similarities = analyzer.calculateAllSimilarities(parseFloat(value));
                    updateStats();
                    if (currentUser) {
                        createHeatmap(currentUser);
                        showSimilarUsers(currentUser);
                        createHistogram();
                    }
                    showProgress(false);
                }, 100);
            }
        });
        
        // 🔄 MOSTRAR/OCULTAR PROGRESO
        function showProgress(show) {
            document.getElementById('progressContainer').style.display = show ? 'block' : 'none';
        }
        
        // 🚀 INICIALIZACIÓN
        console.log('🎯 Visualizador de Similaridad Jaccard iniciado');
        console.log('📝 Cargar un archivo CSV para comenzar');