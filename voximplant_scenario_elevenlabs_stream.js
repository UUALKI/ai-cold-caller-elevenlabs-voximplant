/**
 * 🎙️ AI Cold Caller с ElevenLabs Streaming TTS
 * Максимальная скорость БЕЗ OpenAI Realtime API
 * Работает из России!
 */

require(Modules.ASR);
require(Modules.ElevenLabs);

////////// КОНФИГУРАЦИЯ //////////
const CALLER_ID = '74951183993';
const CONFIDENCE_THRESHOLD = 0.6;
const MAX_RETRIES = 2;
const RESPONSE_TIMEOUT = 4000; // Быстрый режим
const ASR_TIMEOUT = 5000;

// Глобальные переменные
let customDataParsed = {};
let call = undefined;
let asr = undefined;
let elevenLabsPlayer = undefined;
let conversationTurns = 0;
let retryCount = 0;

////////// ОСНОВНАЯ ЛОГИКА //////////

VoxEngine.addEventListener(AppEvents.Started, () => {
    Logger.write("🎙️ ElevenLabs Streaming AI Scenario started!");
    
    const customData = VoxEngine.customData();
    if (customData) {
        Logger.write(`📥 Custom data received: ${customData}`);
        handleCustomData(customData);
    } else {
        Logger.write("❌ No custom data provided. Terminating.");
        VoxEngine.terminate();
    }
});

// Обработка входящих параметров
const handleCustomData = (customData) => {
    try {
        customDataParsed = JSON.parse(customData);
        Logger.write(`✅ Custom data parsed successfully`);
        Logger.write(`📞 Phone: ${customDataParsed.phone}`);
        Logger.write(`🎵 ElevenLabs Voice: ${customDataParsed.voice_id}`);
        
        initiateCall();
        
    } catch (error) {
        Logger.write(`❌ Error parsing custom data: ${error}`);
        VoxEngine.terminate();
    }
};

// Инициализация звонка
const initiateCall = () => {
    Logger.write(`📞 Making outbound call to ${customDataParsed.phone}`);
    
    call = VoxEngine.callPSTN(customDataParsed.phone, CALLER_ID);
    
    call.addEventListener(CallEvents.Connected, handleCallConnected);
    call.addEventListener(CallEvents.Disconnected, handleCallDisconnected);
    call.addEventListener(CallEvents.Failed, handleCallFailed);
    
    call.answer();
};

// Обработчик подключения звонка
const handleCallConnected = async () => {
    Logger.write("✅ Call connected! Initializing ASR and ElevenLabs...");
    
    try {
        await initializeASR();
        await initializeElevenLabs();
        await startConversation();
        
    } catch (error) {
        Logger.write(`❌ Error initializing call systems: ${error}`);
        VoxEngine.terminate();
    }
};

// Инициализация ASR
const initializeASR = async () => {
    try {
        Logger.write("🎤 Initializing ASR...");
        
        asr = VoxEngine.createASR({
            profile: ASRProfileList.Google.ru_RU,
            singleUtterance: false,
            interimResults: false,
            profanityFilter: false,
            maxAlternatives: 3
        });
        
        asr.addEventListener(ASREvents.Started, function() {
            Logger.write('🎤 ASR started successfully');
        });
        
        asr.addEventListener(ASREvents.Result, handleASRResult);
        
        asr.addEventListener(ASREvents.Error, function(e) {
            const errorCode = e && e.code ? e.code : 'unknown';
            const errorMsg = e && e.error ? e.error : 'unknown error';
            Logger.write(`❌ ASR Error: ${errorCode} - ${errorMsg}`);
        });
        
        Logger.write("✅ ASR initialized successfully");
        
    } catch (error) {
        Logger.write(`❌ ASR initialization error: ${error}`);
        throw error;
    }
};

// Инициализация ElevenLabs
const initializeElevenLabs = async () => {
    try {
        Logger.write("🎵 Initializing ElevenLabs Streaming TTS...");
        
        // ElevenLabs уже подключен через require(Modules.ElevenLabs)
        Logger.write("✅ ElevenLabs ready for streaming");
        
    } catch (error) {
        Logger.write(`❌ ElevenLabs initialization error: ${error}`);
        throw error;
    }
};

// Начало разговора
const startConversation = async () => {
    Logger.write("👋 Starting conversation with ElevenLabs streaming...");
    
    const greeting = customDataParsed.greeting || getDefaultGreeting();
    await speakTextStreaming(greeting);
    
    conversationTurns = 0;
    Logger.write("✅ Conversation started");
};

// Обработка результатов ASR
const handleASRResult = function(e) {
    try {
        Logger.write(`🎤 ASR Result received: ${JSON.stringify(e)}`);
        
        if (!e || !e.results || e.results.length === 0) {
            Logger.write("⚠️ No ASR results received");
            handleLowConfidenceOrEmpty("Извините, я вас не расслышала. Не могли бы вы повторить?");
            return;
        }
        
        let bestText = '';
        let bestConfidence = 0;
        
        for (const result of e.results) {
            if (result.alternatives && result.alternatives.length > 0) {
                for (const alt of result.alternatives) {
                    if (alt.confidence > bestConfidence) {
                        bestConfidence = alt.confidence;
                        bestText = alt.transcript || '';
                    }
                }
            }
        }
        
        Logger.write(`🎯 Best result: "${bestText}" (confidence: ${bestConfidence})`);
        
        if (bestConfidence < CONFIDENCE_THRESHOLD) {
            Logger.write(`⚠️ Low confidence, asking for repeat`);
            handleLowConfidenceOrEmpty("Простите, связь не очень хорошая. Не могли бы вы повторить громче?");
            return;
        }
        
        if (!bestText || bestText.trim().length < 2) {
            Logger.write("⚠️ Empty or too short text");
            handleLowConfidenceOrEmpty("Я вас не расслышала. Повторите, пожалуйста.");
            return;
        }
        
        processUserInput(bestText, bestConfidence);
        
    } catch (error) {
        Logger.write(`❌ Error handling ASR result: ${error}`);
        handleLowConfidenceOrEmpty("Извините, произошла техническая ошибка. Повторите, пожалуйста.");
    }
};

// Обработка низкого качества распознавания
const handleLowConfidenceOrEmpty = (fallbackMessage) => {
    retryCount++;
    
    if (retryCount >= MAX_RETRIES) {
        Logger.write(`⚠️ Max retries reached, using smart fallback`);
        const smartFallback = getSmartFallbackResponse();
        speakTextStreaming(smartFallback);
        retryCount = 0;
    } else {
        Logger.write(`🔄 Retry ${retryCount}/${MAX_RETRIES}: ${fallbackMessage}`);
        speakTextStreaming(fallbackMessage);
    }
};

// Обработка пользовательского ввода
const processUserInput = async (userText, confidence) => {
    Logger.write(`🧠 Processing user input: "${userText}" (confidence: ${confidence})`);
    
    retryCount = 0;
    conversationTurns++;
    
    await requestAIResponse(userText);
};

// Быстрый запрос к AI
const requestAIResponse = async (userText) => {
    try {
        Logger.write(`🚀 Fast AI request for: "${userText}"`);
        
        const webhookUrl = customDataParsed.webhook_url;
        if (!webhookUrl) {
            Logger.write("❌ No webhook URL provided");
            speakTextStreaming(getSmartFallbackResponse());
            return;
        }
        
        const requestData = {
            text: userText,
            turn: conversationTurns,
            streaming: true, // Запрашиваем потоковый ответ
            fast: true
        };
        
        Logger.write(`⚡ Streaming request to: ${webhookUrl}`);
        
        const promise = Net.httpRequestAsync(webhookUrl, {
            headers: [
                "Content-Type: application/json",
                "X-Streaming: true",
                "Connection: keep-alive"
            ],
            method: 'POST',
            postData: JSON.stringify(requestData)
        });
        
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Fast timeout')), RESPONSE_TIMEOUT);
        });
        
        const res = await Promise.race([promise, timeoutPromise]);
        
        Logger.write(`📥 AI Response code: ${res.code}`);
        
        if (res.code === 200) {
            try {
                const jsData = JSON.parse(res.text);
                const aiResponse = jsData.response?.text || jsData.text || jsData.message;
                
                if (aiResponse && aiResponse.trim().length > 0) {
                    Logger.write(`🤖 AI response: "${aiResponse}"`);
                    await speakTextStreaming(aiResponse);
                } else {
                    Logger.write("⚠️ Empty AI response, using fallback");
                    await speakTextStreaming(getSmartFallbackResponse());
                }
            } catch (parseError) {
                Logger.write(`❌ JSON parse error: ${parseError}`);
                await speakTextStreaming(getSmartFallbackResponse());
            }
        } else {
            Logger.write(`❌ HTTP error: ${res.code}, using fallback`);
            await speakTextStreaming(getSmartFallbackResponse());
        }
        
    } catch (error) {
        Logger.write(`❌ Request error: ${error}`);
        await speakTextStreaming("Извините, возникли технические проблемы. Давайте я перезвоню вам позже?");
    }
};

// ПОТОКОВЫЙ TTS через ElevenLabs
const speakTextStreaming = async (text) => {
    try {
        Logger.write(`🎵 ElevenLabs streaming: "${text}"`);
        
        // Останавливаем ASR
        if (asr) {
            asr.stop();
        }
        
        // Останавливаем предыдущий плеер если есть
        if (elevenLabsPlayer) {
            elevenLabsPlayer.stop();
        }
        
        // Параметры для ElevenLabs
        const voiceId = customDataParsed.voice_id || customDataParsed.candidate_voice_ids[0] || "pNInz6obpgDQGcFmaJgB";
        
        const pathParameters = {
            voice_id: voiceId
        };
        
        const queryParameters = {
            model_id: 'eleven_flash_v2_5', // Самая быстрая модель
            optimize_streaming_latency: 4, // Максимальная оптимизация
            output_format: 'pcm_16000'
        };
        
        const ttsParameters = {
            pathParameters,
            queryParameters,
            keepAlive: true
        };
        
        // Создаем потоковый плеер ElevenLabs
        elevenLabsPlayer = ElevenLabs.createRealtimeTTSPlayer(text, ttsParameters);
        
        // Отправляем аудио в звонок
        elevenLabsPlayer.sendMediaTo(call);
        
        // Обработчик завершения воспроизведения
        elevenLabsPlayer.addEventListener(PlayerEvents.PlaybackFinished, function() {
            Logger.write("🎵 ElevenLabs playback finished, starting ASR...");
            startASRListening();
        });
        
        // Обработчик ошибок
        elevenLabsPlayer.addEventListener(PlayerEvents.PlaybackError, function(e) {
            Logger.write(`❌ ElevenLabs playback error: ${e.error}`);
            startASRListening(); // Продолжаем работу
        });
        
    } catch (error) {
        Logger.write(`❌ ElevenLabs streaming error: ${error}`);
        // Fallback на простое сообщение
        startASRListening();
    }
};

// Умный ответ-заглушка
const getSmartFallbackResponse = () => {
    const responses = [
        "Понимаю. Расскажите, с какими сложностями в логистике вы сталкиваетесь сейчас?",
        "Интересно. А какой объем грузов вы обычно перевозите из Китая?",
        "Хорошо. Какие у вас основные требования к доставке?",
        "Понятно. Можете рассказать больше о вашем бизнесе?",
        "Отлично. Какие сроки доставки для вас критичны?"
    ];
    
    const randomIndex = Math.floor(Math.random() * responses.length);
    return responses[randomIndex];
};

// Приветствие по умолчанию
const getDefaultGreeting = () => {
    return "Здравствуйте! Меня зовут Анна, я звоню из компании ТРАНСТИРЕКС по логистике. У нас есть отличное предложение по оптимизации ваших поставок из Китая. Могу рассказать подробнее?";
};

// Запуск прослушивания ASR
const startASRListening = () => {
    try {
        if (asr && call) {
            Logger.write("🎤 Starting ASR listening...");
            call.sendMediaTo(asr);
            
            setTimeout(() => {
                if (asr) {
                    Logger.write("⏰ ASR timeout, prompting user");
                    speakTextStreaming("Вы меня слышите? Если да, скажите что-нибудь.");
                }
            }, ASR_TIMEOUT);
        }
    } catch (error) {
        Logger.write(`❌ Error starting ASR: ${error}`);
    }
};

// Обработчики завершения звонка
const handleCallDisconnected = () => {
    Logger.write("📞 Call disconnected");
    cleanup();
};

const handleCallFailed = (e) => {
    const reason = e && e.reason ? e.reason : 'unknown reason';
    Logger.write(`❌ Call failed: ${reason}`);
    cleanup();
};

// Очистка ресурсов
const cleanup = () => {
    if (asr) {
        asr.stop();
    }
    if (elevenLabsPlayer) {
        elevenLabsPlayer.stop();
    }
    VoxEngine.terminate();
};

Logger.write("🎙️ ElevenLabs Streaming AI Scenario loaded and ready");
