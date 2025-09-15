/**
 * 🤖 ElevenLabs AI Agent Integration
 * 🎭 Интеграция с ElevenLabs AI Agent Platform
 * 📞 Реальные звонки с российских номеров
 * 🧠 Умный диалог через ElevenLabs Agent
 */

require(Modules.ASR);
require(Modules.ElevenLabs);

////////// КОНФИГУРАЦИЯ //////////
const CALLER_ID = '74951183993'; // Номер из config.py
const CONFIDENCE_THRESHOLD = 0.6;
const RECOGNITION_TIMEOUT = 8000;

// Глобальные переменные
let customDataParsed = {};
let call = undefined;
let elevenLabsPlayer = undefined;
let conversationTurns = 0;
let isBotSpeaking = false;
let isProcessingAudio = false;
let currentASR = null;
let asrTimeoutId = null;
let playerTimeoutId = null;
let callStartTime = null;
let conversationSessionId = null;
let conversationHistory = [];

////////// АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ //////////

VoxEngine.addEventListener(AppEvents.Started, () => {
    Logger.write("🤖 ElevenLabs AI Agent Integration запущен!");
    Logger.write("🎭 Интеграция с ElevenLabs Agent Platform");
    
    const customData = VoxEngine.customData();
    if (customData) {
        handleCustomData(customData);
    } else {
        Logger.write("❌ No custom data provided. Terminating.");
        VoxEngine.terminate();
    }
});

const handleCustomData = (customData) => {
    try {
        customDataParsed = JSON.parse(customData);
        callStartTime = Date.now();
        conversationSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        Logger.write(`✅ Конфигурация загружена для: ${customDataParsed.phone}`);
        Logger.write(`🎭 Agent ID: ${customDataParsed.agent_id}`);
        Logger.write(`🔑 API Key: ${customDataParsed.api_key ? customDataParsed.api_key.substring(0, 20) + '...' : 'Not provided'}`);
        
        // Проверяем доступность агента перед звонком
        checkAgentAvailability().then(() => {
            initiateCall();
        }).catch((error) => {
            Logger.write(`❌ Agent недоступен: ${error}`);
            VoxEngine.terminate();
        });
        
    } catch (error) {
        Logger.write(`❌ Config error: ${error}`);
        VoxEngine.terminate();
    }
};

const checkAgentAvailability = async () => {
    try {
        const agentId = customDataParsed.agent_id;
        const apiKey = customDataParsed.api_key;
        
        if (!agentId || !apiKey) {
            throw new Error("Missing agent_id or api_key");
        }
        
        const url = `https://api.elevenlabs.io/v1/agent/${agentId}`;
        
        Logger.write(`🔍 Проверяем доступность агента: ${agentId}`);
        
        const response = await Net.httpRequestAsync(url, {
            method: 'GET',
            headers: [
                'Content-Type: application/json',
                `xi-api-key: ${apiKey}`
            ]
        });
        
        Logger.write(`📡 Agent check response code: ${response.code}`);
        
        if (response.code === 200) {
            const agentData = JSON.parse(response.body);
            Logger.write(`✅ Agent доступен: ${agentData.name || agentId}`);
            return true;
        } else {
            throw new Error(`Agent check failed: ${response.code} - ${response.body}`);
        }
        
    } catch (error) {
        Logger.write(`❌ Ошибка проверки агента: ${error}`);
        throw error;
    }
};

const initiateCall = () => {
    Logger.write(`📞 Звонок: ${customDataParsed.phone}`);
    
    call = VoxEngine.callPSTN(customDataParsed.phone, CALLER_ID);
    
    call.addEventListener(CallEvents.Connected, startElevenLabsConversation);
    call.addEventListener(CallEvents.Disconnected, saveAndCleanup);
    call.addEventListener(CallEvents.Failed, saveAndCleanup);
    
    call.answer();
};

////////// 🎭 ELEVENLABS AGENT ИНТЕГРАЦИЯ //////////

const startElevenLabsConversation = async () => {
    Logger.write("🎭 Начинаем диалог с ElevenLabs AI Agent");
    
    try {
        // Отправляем приветствие в ElevenLabs Agent
        const greeting = await callElevenLabsAgent("", "greeting");
        
        // Добавляем в историю
        conversationHistory.push({
            role: "agent",
            text: greeting,
            timestamp: new Date().toISOString()
        });
        
        Logger.write(`🤖 Agent приветствие: "${greeting}"`);
        
        // Воспроизводим приветствие
        await speakElevenLabsResponse(greeting);
        
        // Запускаем прослушивание клиента
        setTimeout(startListening, 500);
        
    } catch (error) {
        Logger.write(`❌ Ошибка запуска диалога: ${error}`);
        VoxEngine.terminate();
    }
};

const callElevenLabsAgent = async (userMessage, messageType = "user_input") => {
    try {
        const agentId = customDataParsed.agent_id;
        const apiKey = customDataParsed.api_key;
        
        if (!agentId || !apiKey) {
            throw new Error("Missing agent_id or api_key");
        }
        
        const url = `https://api.elevenlabs.io/v1/agent/${agentId}/conversation`;
        
        const requestData = {
            session_id: conversationSessionId,
            message_type: messageType,
            message: userMessage || "",
            voice_id: customDataParsed.voice_id || "21m00Tcm4TlvDq8ikWAM"
        };
        
        Logger.write(`🌐 Отправляем запрос в ElevenLabs Agent: ${messageType}`);
        Logger.write(`🔗 URL: ${url}`);
        Logger.write(`📝 Request data: ${JSON.stringify(requestData)}`);
        Logger.write(`🔑 API Key (first 10 chars): ${apiKey.substring(0, 10)}...`);
        
        const response = await Net.httpRequestAsync(url, {
            method: 'POST',
            headers: [
                'Content-Type: application/json',
                `xi-api-key: ${apiKey}`
            ],
            postData: JSON.stringify(requestData)
        });
        
        Logger.write(`📡 ElevenLabs API response code: ${response.code}`);
        Logger.write(`📡 Response headers: ${JSON.stringify(response.headers)}`);
        Logger.write(`📡 Response body: ${response.body}`);
        
        if (response.code === 200) {
            const result = JSON.parse(response.body);
            const agentResponse = result.response || result.message || "Извините, произошла ошибка";
            
            Logger.write(`✅ ElevenLabs Agent ответ получен: ${agentResponse.substring(0, 50)}...`);
            return agentResponse;
            
        } else {
            Logger.write(`❌ ElevenLabs API error: ${response.code} - ${response.body}`);
            
            // Детальная обработка ошибок
            if (response.code === 401) {
                Logger.write("❌ Ошибка аутентификации - проверьте API ключ");
                return "Извините, техническая ошибка аутентификации.";
            } else if (response.code === 404) {
                Logger.write("❌ Agent не найден - проверьте agent_id");
                return "Извините, агент не найден.";
            } else if (response.code === 429) {
                Logger.write("❌ Превышен лимит запросов");
                return "Извините, превышен лимит запросов. Попробуйте позже.";
            } else {
                return "Извините, техническая ошибка. Попробуйте позже.";
            }
        }
        
    } catch (error) {
        Logger.write(`❌ Ошибка вызова ElevenLabs Agent: ${error}`);
        Logger.write(`❌ Error stack: ${error.stack || 'No stack trace'}`);
        return "Извините, не могу обработать запрос. Попробуйте еще раз.";
    }
};

////////// 🎤 ASR ЛОГИКА //////////

const startListening = () => {
    if (isBotSpeaking || isProcessingAudio) {
        Logger.write("🎤 Пропуск прослушивания - бот говорит или обрабатывается аудио");
        return;
    }
    
    if (currentASR) {
        currentASR.stop();
    }
    
    try {
        currentASR = VoxEngine.createASR({
            lang: 'ru-RU',
            mode: ASRMode.SINGLE_UTTERANCE,
            timeout: RECOGNITION_TIMEOUT
        });
        
        currentASR.addEventListener(ASREvents.Result, handleASRResult);
        currentASR.addEventListener(ASREvents.Error, handleASRError);
        currentASR.addEventListener(ASREvents.Timeout, handleASRTimeout);
        
        currentASR.start();
        Logger.write("🎤 Начинаем прослушивание клиента");
        
        // Таймаут для ASR
        asrTimeoutId = setTimeout(() => {
            if (currentASR) {
                Logger.write("⏰ ASR таймаут - останавливаем прослушивание");
                currentASR.stop();
            }
        }, RECOGNITION_TIMEOUT + 2000);
        
    } catch (error) {
        Logger.write(`❌ Ошибка создания ASR: ${error}`);
        setTimeout(startListening, 2000);
    }
};

const handleASRResult = async (event) => {
    if (asrTimeoutId) {
        clearTimeout(asrTimeoutId);
        asrTimeoutId = null;
    }
    
    const userText = event.text;
    const confidence = event.confidence || 0;
    
    Logger.write(`👤 Клиент сказал: "${userText}" (confidence: ${confidence})`);
    
    if (userText && userText.trim().length > 0 && confidence >= CONFIDENCE_THRESHOLD) {
        conversationTurns++;
        
        // Добавляем в историю
        conversationHistory.push({
            role: "client",
            text: userText,
            timestamp: new Date().toISOString(),
            confidence: confidence
        });
        
        isProcessingAudio = true;
        
        try {
            // Отправляем в ElevenLabs Agent
            const agentResponse = await callElevenLabsAgent(userText, "user_input");
            
            // Добавляем ответ в историю
            conversationHistory.push({
                role: "agent",
                text: agentResponse,
                timestamp: new Date().toISOString()
            });
            
            // Воспроизводим ответ
            await speakElevenLabsResponse(agentResponse);
            
        } catch (error) {
            Logger.write(`❌ Ошибка обработки ответа клиента: ${error}`);
            await speakElevenLabsResponse("Извините, произошла ошибка. Попробуйте еще раз.");
        } finally {
            isProcessingAudio = false;
        }
        
    } else if (userText && userText.trim().length > 0) {
        Logger.write(`⚠️ Низкая уверенность ASR: ${confidence}`);
        await speakElevenLabsResponse("Извините, не расслышал. Можете повторить?");
        setTimeout(startListening, 1000);
        
    } else {
        Logger.write("🔇 Пустой результат ASR");
        setTimeout(startListening, 1000);
    }
};

const handleASRError = (event) => {
    if (asrTimeoutId) {
        clearTimeout(asrTimeoutId);
        asrTimeoutId = null;
    }
    
    Logger.write(`❌ ASR ошибка: ${event.error}`);
    setTimeout(startListening, 2000);
};

const handleASRTimeout = () => {
    if (asrTimeoutId) {
        clearTimeout(asrTimeoutId);
        asrTimeoutId = null;
    }
    
    Logger.write("⏰ ASR таймаут - клиент не сказал ничего");
    
    // Если это первый ход, прощаемся
    if (conversationTurns === 0) {
        speakElevenLabsResponse("Извините, не удалось связаться. Попробуйте позже. До свидания!");
        setTimeout(() => VoxEngine.terminate(), 3000);
    } else {
        // Продолжаем диалог
        setTimeout(startListening, 1000);
    }
};

////////// 🎵 ELEVENLABS TTS //////////

const speakElevenLabsResponse = async (text) => {
    if (isBotSpeaking) {
        Logger.write("🎵 Пропуск TTS - бот уже говорит");
        return;
    }
    
    try {
        Logger.write(`🤖 Воспроизводим ответ: "${text.substring(0, 50)}..."`);
        
        isBotSpeaking = true;
        
        const voiceId = customDataParsed.voice_id || "21m00Tcm4TlvDq8ikWAM";
        
        const ttsParameters = {
            voice_id: voiceId,
            model_id: "eleven_multilingual_v2",
            voice_settings: {
                stability: 0.5,
                similarity_boost: 0.75
            }
        };
        
        elevenLabsPlayer = ElevenLabs.createRealtimeTTSPlayer(text, ttsParameters);
        
        if (!elevenLabsPlayer) {
            throw new Error("Failed to create TTS player");
        }
        
        // Обработчики событий TTS
        elevenLabsPlayer.addEventListener(PlayerEvents.Started, () => {
            Logger.write("🎵 TTS воспроизведение началось");
        });
        
        elevenLabsPlayer.addEventListener(PlayerEvents.PlaybackFinished, () => {
            Logger.write("🎵 TTS воспроизведение завершено");
            
            if (playerTimeoutId) {
                clearTimeout(playerTimeoutId);
                playerTimeoutId = null;
            }
            
            isBotSpeaking = false;
            
            // Продолжаем диалог
            setTimeout(() => {
                if (!isBotSpeaking) {
                    startListening();
                }
            }, 500);
        });
        
        elevenLabsPlayer.addEventListener(PlayerEvents.PlaybackError, (event) => {
            Logger.write(`❌ TTS ошибка: ${event.error || 'Unknown error'}`);
            isBotSpeaking = false;
            setTimeout(startListening, 1000);
        });
        
        // Отправляем аудио в звонок
        if (elevenLabsPlayer && call) {
            elevenLabsPlayer.sendMediaTo(call);
            Logger.write("🎵 TTS аудио отправлено в звонок");
            
            // Backup таймер на случай зависания
            playerTimeoutId = setTimeout(() => {
                if (isBotSpeaking) {
                    Logger.write("⏰ TTS backup таймер - принудительно завершаем");
                    isBotSpeaking = false;
                    setTimeout(startListening, 500);
                }
            }, 10000);
            
        } else {
            throw new Error("TTS player or call not available");
        }
        
    } catch (error) {
        Logger.write(`❌ Ошибка TTS: ${error}`);
        isBotSpeaking = false;
        setTimeout(startListening, 1000);
    }
};

////////// 📊 СОХРАНЕНИЕ ДАННЫХ //////////

const saveAndCleanup = async () => {
    Logger.write("💾 Сохраняем данные звонка и очищаем ресурсы");
    
    try {
        const callDuration = Math.round((Date.now() - callStartTime) / 1000);
        
        const callData = {
            call_id: conversationSessionId,
            phone_number: customDataParsed.phone,
            start_time: new Date(callStartTime).toISOString(),
            end_time: new Date().toISOString(),
            duration: callDuration,
            status: "completed",
            conversation: conversationHistory,
            conversation_turns: conversationTurns,
            agent_id: customDataParsed.agent_id,
            outcome: analyzeOutcome(conversationHistory),
            metrics: analyzeMetrics(conversationHistory, callDuration)
        };
        
        // Отправляем данные через webhook
        const webhookUrl = customDataParsed.webhook_url || "http://localhost:8000/api/call-results";
        
        Logger.write(`📡 Отправляем данные в webhook: ${webhookUrl}`);
        
        const response = await Net.httpRequestAsync(webhookUrl, {
            method: 'POST',
            headers: ['Content-Type: application/json'],
            postData: JSON.stringify(callData)
        });
        
        Logger.write(`✅ Данные отправлены. Response code: ${response.code}`);
        
    } catch (error) {
        Logger.write(`❌ Ошибка сохранения данных: ${error}`);
    }
    
    // Очистка ресурсов
    if (currentASR) {
        currentASR.stop();
    }
    
    if (asrTimeoutId) {
        clearTimeout(asrTimeoutId);
    }
    
    if (playerTimeoutId) {
        clearTimeout(playerTimeoutId);
    }
    
    VoxEngine.terminate();
};

////////// 📈 АНАЛИЗ РЕЗУЛЬТАТОВ //////////

const analyzeOutcome = (conversation) => {
    if (conversation.length === 0) return "no_conversation";
    
    const lastClientMessage = conversation
        .filter(msg => msg.role === "client")
        .pop()?.text.toLowerCase() || "";
    
    if (lastClientMessage.includes("интересно") || 
        lastClientMessage.includes("давайте") || 
        lastClientMessage.includes("хорошо") ||
        lastClientMessage.includes("да")) {
        return "interested";
    } else if (lastClientMessage.includes("не интересует") || 
               lastClientMessage.includes("нет") ||
               lastClientMessage.includes("не нужно")) {
        return "not_interested";
    } else if (lastClientMessage.includes("позже") ||
               lastClientMessage.includes("не сейчас")) {
        return "maybe_later";
    } else {
        return "neutral";
    }
};

const analyzeMetrics = (conversation, duration) => {
    const clientMessages = conversation.filter(msg => msg.role === "client");
    const agentMessages = conversation.filter(msg => msg.role === "agent");
    
    let engagement = "low";
    if (clientMessages.length >= 3) engagement = "high";
    else if (clientMessages.length >= 1) engagement = "medium";
    
    let sentiment = "neutral";
    const positiveWords = ["интересно", "хорошо", "да", "давайте", "отлично"];
    const negativeWords = ["не интересует", "нет", "не нужно", "дорого"];
    
    const allClientText = clientMessages.map(msg => msg.text.toLowerCase()).join(" ");
    
    const positiveCount = positiveWords.filter(word => allClientText.includes(word)).length;
    const negativeCount = negativeWords.filter(word => allClientText.includes(word)).length;
    
    if (positiveCount > negativeCount) sentiment = "positive";
    else if (negativeCount > positiveCount) sentiment = "negative";
    
    return {
        turns: conversation.length,
        client_turns: clientMessages.length,
        agent_turns: agentMessages.length,
        engagement: engagement,
        sentiment: sentiment,
        avg_response_time: duration / Math.max(conversation.length, 1),
        key_topics: extractKeyTopics(conversation)
    };
};

const extractKeyTopics = (conversation) => {
    const topics = [];
    const allText = conversation.map(msg => msg.text.toLowerCase()).join(" ");
    
    if (allText.includes("цена") || allText.includes("стоимость")) topics.push("pricing");
    if (allText.includes("срок") || allText.includes("время")) topics.push("timing");
    if (allText.includes("качество") || allText.includes("надежность")) topics.push("quality");
    if (allText.includes("компания") || allText.includes("о вас")) topics.push("company_info");
    
    return topics;
};

////////// 🧹 ОЧИСТКА //////////

const cleanup = () => {
    Logger.write("🧹 Очистка ресурсов ElevenLabs Agent");
    
    if (currentASR) {
        currentASR.stop();
    }
    
    if (asrTimeoutId) {
        clearTimeout(asrTimeoutId);
    }
    
    if (playerTimeoutId) {
        clearTimeout(playerTimeoutId);
    }
    
    VoxEngine.terminate();
};
