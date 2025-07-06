/**
 * NameSmithy Frontend JavaScript - Ultra Compatible Version
 * Compatible with all browsers including older versions
 */

function NameSmithy() {
    this.apiEndpoint = '/api';
    this.isInitialized = false;
    
    // Bind methods to this
    var self = this;
    
    // Initialize when called
    this.init = function() {
        console.log('🔨 NameSmithy initializing...');
        self.initEventListeners();
        self.checkApiStatus();
    };
    
    this.checkApiStatus = function() {
        console.log('🔍 Checking API status...');
        // Use XMLHttpRequest for maximum compatibility
        var xhr = new XMLHttpRequest();
        xhr.open('GET', self.apiEndpoint + '/status', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        var data = JSON.parse(xhr.responseText);
                        if (data.status === 'online' && data.gbr_loaded) {
                            console.log('✅ API is online with working models');
                            console.log('📊 Loaded ' + data.known_names_count + ' known names');
                            self.isInitialized = true;
                        } else {
                            console.warn('⚠️ API models not loaded properly');
                        }
                    } catch (e) {
                        console.error('❌ Failed to parse API status response');
                    }
                } else {
                    console.warn('⚠️ API not available, status: ' + xhr.status);
                }
            }
        };
        xhr.send();
    };
    
    this.initEventListeners = function() {
        console.log('🔧 Setting up event listeners...');
        
        // Navigation
        var startBtn = document.getElementById('start-btn');
        if (startBtn) {
            startBtn.onclick = function() {
                var generator = document.getElementById('generator');
                if (generator && generator.scrollIntoView) {
                    generator.scrollIntoView();
                }
            };
        }
        
        // Generator
        var generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.onclick = function() {
                self.generateNames();
            };
        }
        
        var regenerateBtn = document.getElementById('regenerate-btn');
        if (regenerateBtn) {
            regenerateBtn.onclick = function() {
                self.generateNames();
            };
        }
        
        var exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.onclick = function() {
                self.exportResults();
            };
        }
        
        // Evaluator
        var evaluateBtn = document.getElementById('evaluate-btn');
        if (evaluateBtn) {
            evaluateBtn.onclick = function() {
                self.evaluateName();
            };
        }
        
        var evalNameInput = document.getElementById('eval-name');
        if (evalNameInput) {
            evalNameInput.onkeypress = function(e) {
                if (e.keyCode === 13 || e.which === 13) { // Enter key
                    self.evaluateName();
                }
            };
        }
        
        console.log('✅ Event listeners set up');
    };
    
    this.evaluateName = function() {
        console.log('🔍 Starting name evaluation...');
        
        var nameInput = document.getElementById('eval-name');
        var genderSelect = document.getElementById('eval-gender');
        
        if (!nameInput || !genderSelect) {
            console.error('❌ Required form elements not found');
            alert('Form elements not found');
            return;
        }
        
        var name = nameInput.value;
        var gender = genderSelect.value;
        
        // Clean up the name
        if (name) {
            name = name.replace(/^\s+|\s+$/g, ''); // trim whitespace
        }
        
        if (!name) {
            console.warn('⚠️ No name entered');
            alert('Please enter a name to evaluate.');
            return;
        }
        
        console.log('🔍 Evaluating name: "' + name + '" gender: "' + gender + '"');
        
        // Use XMLHttpRequest for maximum compatibility
        var xhr = new XMLHttpRequest();
        xhr.open('POST', self.apiEndpoint + '/evaluate', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = function() {
            console.log('📡 XHR state changed: ' + xhr.readyState + ', status: ' + xhr.status);
            
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        console.log('📊 Raw response: ' + xhr.responseText);
                        var data = JSON.parse(xhr.responseText);
                        console.log('📊 Parsed response:', data);
                        
                        if (data.success && data.result) {
                            console.log('✅ Success! Displaying result');
                            self.displayEvaluation(data.result);
                        } else {
                            console.error('❌ API returned success=false: ' + (data.error || 'Unknown error'));
                            alert('Failed to evaluate name: ' + (data.error || 'Unknown error'));
                        }
                    } catch (e) {
                        console.error('💥 Error parsing JSON response: ' + e.message);
                        console.error('💥 Raw response was: ' + xhr.responseText);
                        alert('Failed to parse server response');
                    }
                } else {
                    console.error('💥 HTTP error: ' + xhr.status);
                    alert('Server error: ' + xhr.status);
                }
            }
        };
        
        var requestData = JSON.stringify({
            name: name,
            gender: gender
        });
        
        console.log('📡 Sending request: ' + requestData);
        xhr.send(requestData);
    };
    
    this.displayEvaluation = function(result) {
        console.log('🎯 Displaying evaluation result:', result);
        
        try {
            // Update name display
            var nameDisplay = document.getElementById('eval-name-display');
            if (nameDisplay) {
                nameDisplay.innerHTML = result.name || 'Unknown';
                console.log('✅ Set name display');
            }
            
            // Update score
            var scoreValue = document.getElementById('score-value');
            if (scoreValue) {
                var score = result.score || result.predicted_score || 50;
                scoreValue.innerHTML = score;
                console.log('✅ Set score value: ' + score);
            }
            
            // Update description
            var scoreDescription = document.getElementById('score-description');
            if (scoreDescription) {
                var description = 'Predicted Score: ' + (result.quality_tier || self.getScoreDescription(score));
                scoreDescription.innerHTML = description;
                console.log('✅ Set score description');
            }
            
            // Update popularity info
            var popularityInfo = document.getElementById('popularity-info');
            if (popularityInfo) {
                var popularity = 'Historical: ' + (result.known_rank || 'Not found');
                popularityInfo.innerHTML = popularity;
                console.log('✅ Set popularity info');
            }
            
            // Update quality flags
            var flagsContainer = document.getElementById('quality-flags');
            if (flagsContainer) {
                flagsContainer.innerHTML = '';
                
                // Check for inappropriate content
                if (result.appropriate === false || result.quality_tier === 'Inappropriate') {
                    var flagElement = document.createElement('span');
                    flagElement.className = 'flag inappropriate';
                    flagElement.innerHTML = '⚠️ Inappropriate';
                    flagsContainer.appendChild(flagElement);
                    console.log('✅ Added inappropriate flag');
                }
            }
            
            // Show result section
            var evalResult = document.getElementById('eval-result');
            if (evalResult) {
                evalResult.className = evalResult.className.replace(/\bhidden\b/g, '');
                console.log('✅ Showed result section');
            }
            
            console.log('🎉 Evaluation display completed successfully!');
            
        } catch (error) {
            console.error('💥 Error in displayEvaluation: ' + error.message);
            alert('Error displaying results: ' + error.message);
        }
    };
    
    this.getScoreDescription = function(score) {
        if (score >= 80) return 'Excellent';
        if (score >= 70) return 'Very Good';
        if (score >= 50) return 'Good';
        if (score >= 30) return 'Fair';
        return 'Poor';
    };
    
    this.generateNames = function() {
        console.log('🎯 Starting name generation...');
        
        var countInput = document.getElementById('count');
        var genderSelect = document.getElementById('gender');
        var styleSelect = document.getElementById('style');
        var minScoreInput = document.getElementById('min-score');
        var maxScoreInput = document.getElementById('max-score');
        
        if (!countInput || !genderSelect || !styleSelect || !minScoreInput || !maxScoreInput) {
            console.error('❌ Required form elements not found');
            alert('Form elements not found');
            return;
        }
        
        var count = parseInt(countInput.value) || 5;
        var gender = genderSelect.value;
        var style = styleSelect.value;
        var minScore = parseInt(minScoreInput.value) || 70;
        var maxScore = parseInt(maxScoreInput.value) || 100;
        
        console.log('🎯 Generating ' + count + ' ' + gender + ' names with style "' + style + '" and score range ' + minScore + '-' + maxScore);
        
        // Store generation state
        self.isGenerating = true;
        self.generationTarget = count;
        self.generationStartTime = Date.now();
        
        // Show loading state with progress
        var loadingDiv = document.getElementById('loading');
        var resultsDiv = document.getElementById('results');
        var generateBtn = document.getElementById('generate-btn');
        var progressDetails = document.getElementById('progress-details');
        var abortBtn = document.getElementById('abort-btn');
        
        if (loadingDiv) {
            loadingDiv.className = loadingDiv.className.replace(/\bhidden\b/g, '');
        }
        if (resultsDiv) {
            resultsDiv.className = resultsDiv.className + ' hidden';
        }
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = 'Generating...';
        }
        if (progressDetails) {
            progressDetails.innerHTML = 'Target: ' + count + ' names, Found: 0, Attempts: 0';
        }
        
        // Set up abort button
        if (abortBtn) {
            abortBtn.onclick = function() {
                self.abortGeneration();
            };
        }
        
        
        // Start generation with new session-based API
        var xhr = new XMLHttpRequest();
        self.currentXHR = xhr;
        xhr.open('POST', self.apiEndpoint + '/generate', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        console.log('📊 Raw generation response:', xhr.responseText);
                        var data = JSON.parse(xhr.responseText);
                        console.log('📊 Parsed generation response:', data);
                        
                        if (data.success && data.session_id) {
                            console.log('✅ Generation started, session:', data.session_id);
                            self.currentSessionId = data.session_id;
                            self.startProgressPolling();
                        } else {
                            console.error('❌ Failed to start generation. Success:', data.success, 'SessionID:', data.session_id, 'Error:', data.error);
                            self.stopGeneration();
                            alert('Failed to start generation: ' + (data.error || 'Unknown error'));
                        }
                    } catch (e) {
                        console.error('💥 Error parsing response:', e);
                        console.error('💥 Raw response was:', xhr.responseText);
                        self.stopGeneration();
                        alert('Failed to parse server response');
                    }
                } else {
                    console.error('💥 HTTP error:', xhr.status);
                    self.stopGeneration();
                    alert('Server error: ' + xhr.status);
                }
            }
        };
        
        var requestData = JSON.stringify({
            count: count,
            gender: gender,
            style: style,
            min_score: minScore,
            max_score: maxScore
        });
        
        console.log('📡 Starting generation with request:', requestData);
        xhr.send(requestData);
    };
    
    this.displayGeneratedNames = function(names) {
        console.log('🎯 Displaying generated names:', names);
        console.log('🔧 DEBUG - Number of names to display:', names.length);
        
        try {
            var container = document.getElementById('names-container');
            if (!container) {
                console.error('❌ Names container not found');
                return;
            }
            
            console.log('🔧 DEBUG - Found names container, clearing content');
            // Clear existing content
            container.innerHTML = '';
            
            // Create name elements
            console.log('🔧 DEBUG - Creating name elements...');
            for (var i = 0; i < names.length; i++) {
                var nameData = names[i];
                console.log('🔧 DEBUG - Processing name ' + (i+1) + ':', nameData);
                var nameElement = self.createNameElement(nameData);
                container.appendChild(nameElement);
            }
            
            // Show results
            var resultsDiv = document.getElementById('results');
            if (resultsDiv) {
                console.log('🔧 DEBUG - Showing results div');
                resultsDiv.className = resultsDiv.className.replace(/\bhidden\b/g, '');
            } else {
                console.error('❌ Results div not found');
            }
            
            console.log('🎉 Generated names display completed successfully!');
            
        } catch (error) {
            console.error('💥 Error displaying generated names: ' + error.message);
            alert('Error displaying results: ' + error.message);
        }
    };
    
    this.createNameElement = function(nameData) {
        var div = document.createElement('div');
        div.className = 'name-item';
        
        var score = nameData.score || nameData.predicted_score || 50;
        var scoreClass = score >= 70 ? 'score-high' : 
                        score >= 50 ? 'score-medium' : 
                        score >= 30 ? 'score-low' : 'score-unknown';
        
        // Handle inappropriate names
        var isInappropriate = !nameData.appropriate || nameData.quality_tier === 'Inappropriate';
        var displayClass = isInappropriate ? 'name-item inappropriate' : 'name-item';
        
        div.className = displayClass;
        div.innerHTML = 
            '<div class="name-info">' +
                '<h5>' + nameData.name + '</h5>' +
                '<p>' + (nameData.quality_tier || 'Unknown') + ' • ' + (nameData.known_rank || 'Not found') + '</p>' +
                (isInappropriate ? '<p class="inappropriate-warning">⚠️ Inappropriate</p>' : '') +
            '</div>' +
            '<div class="name-score">' +
                '<span class="score-badge ' + scoreClass + '">' + score + '</span>' +
            '</div>';
        
        return div;
    };
    
    this.exportResults = function() {
        alert('Export not implemented yet');
    };
    
    this.startProgressPolling = function() {
        self.progressInterval = setInterval(function() {
            if (!self.isGenerating || !self.currentSessionId) {
                clearInterval(self.progressInterval);
                return;
            }
            
            // Poll server for progress
            var xhr = new XMLHttpRequest();
            xhr.open('GET', self.apiEndpoint + '/generate/status/' + self.currentSessionId, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var status = JSON.parse(xhr.responseText);
                            console.log('📊 Status update:', status);
                            self.updateProgress(status);
                            
                            if (status.status === 'completed') {
                                console.log('🎉 Generation completed, results:', status.results);
                                self.onGenerationComplete(status.results);
                            } else if (status.status === 'error') {
                                console.error('❌ Generation error:', status.error);
                                self.onGenerationError(status.error);
                            } else if (status.status === 'aborted') {
                                console.log('🛑 Generation aborted');
                                self.onGenerationAborted(status.results);
                            }
                        } catch (e) {
                            console.error('💥 Error parsing status response:', e);
                            console.error('💥 Raw status response:', xhr.responseText);
                        }
                    } else {
                        console.error('💥 Status poll HTTP error:', xhr.status);
                    }
                }
            };
            xhr.send();
        }, 1000);
    };
    
    this.updateProgress = function(status) {
        var progressDetails = document.getElementById('progress-details');
        if (progressDetails) {
            var progressText = 'Target: ' + status.target + 
                             ', Found: ' + status.found + 
                             ', Attempts: ' + status.attempts + 
                             ' | Elapsed: ' + status.elapsed + 's';
            progressDetails.innerHTML = progressText;
        }
    };
    
    this.stopGeneration = function() {
        self.isGenerating = false;
        if (self.progressInterval) {
            clearInterval(self.progressInterval);
        }
        
        var loadingDiv = document.getElementById('loading');
        var generateBtn = document.getElementById('generate-btn');
        
        if (loadingDiv) {
            loadingDiv.className = loadingDiv.className + ' hidden';
        }
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Generate Names';
        }
    };
    
    this.onGenerationComplete = function(results) {
        console.log('🎉 Generation completed with ' + results.length + ' names');
        self.stopGeneration();
        self.displayGeneratedNames(results);
    };
    
    this.onGenerationError = function(error) {
        console.error('❌ Generation error:', error);
        self.stopGeneration();
        alert('Generation failed: ' + error);
    };
    
    this.onGenerationAborted = function(partialResults) {
        console.log('🛑 Generation was aborted');
        console.log('🔧 DEBUG - onGenerationAborted called with:', partialResults);
        
        if (partialResults && partialResults.length > 0) {
            console.log('📝 Showing ' + partialResults.length + ' partial results');
            console.log('🔧 DEBUG - About to call displayGeneratedNames with:', partialResults);
            self.displayGeneratedNames(partialResults);
        } else {
            console.log('🛑 No partial results to show');
        }
        
        // Stop generation after showing results to avoid hiding them
        self.stopGeneration();
    };
    
    this.abortGeneration = function() {
        console.log('🛑 Requesting abort...');
        
        if (self.currentSessionId) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', self.apiEndpoint + '/generate/abort/' + self.currentSessionId, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            console.log('✅ Abort request successful');
                            console.log('🔧 DEBUG - Abort response:', response);
                            
                            // Immediately show partial results if available
                            console.log('🔧 DEBUG - Full abort response:', response);
                            if (response.partial_results && response.partial_results.length > 0) {
                                console.log('📝 Immediately showing ' + response.partial_results.length + ' partial results');
                                console.log('🔧 DEBUG - Partial results data:', response.partial_results);
                                self.onGenerationAborted(response.partial_results);
                            } else {
                                console.log('🛑 No partial results available');
                                console.log('🔧 DEBUG - Response partial_results:', response.partial_results);
                                self.onGenerationAborted([]);
                            }
                        } catch (e) {
                            console.error('Error parsing abort response:', e);
                            self.stopGeneration();
                        }
                    } else {
                        console.error('❌ Abort request failed');
                        self.stopGeneration();
                        alert('Failed to abort generation');
                    }
                }
            };
            xhr.send();
        } else {
            self.stopGeneration();
        }
    };
}

// Initialize when page loads - compatible with older browsers
if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Page loaded, starting NameSmithy...');
        var app = new NameSmithy();
        app.init();
    });
} else if (document.attachEvent) {
    // IE8 and older
    document.attachEvent('onreadystatechange', function() {
        if (document.readyState === 'complete') {
            console.log('🚀 Page loaded (IE), starting NameSmithy...');
            var app = new NameSmithy();
            app.init();
        }
    });
} else {
    // Very old browsers
    window.onload = function() {
        console.log('🚀 Page loaded (legacy), starting NameSmithy...');
        var app = new NameSmithy();
        app.init();
    };
}