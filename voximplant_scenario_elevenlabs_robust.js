/**
 * Устойчивый сценарий ElevenLabs с официальным модулем Voximplant
 * Автоматическое переподключение и обработка разрывов соединения
 */

// Подключаем официальный модуль ElevenLabs
require(Modules.ElevenLabs);

// Конфигурация
const ELEVENLABS_AGENT_ID = 'agent_01jxd1arjvfq9bd1ae6j92cs3t';
const CALLER_ID = '+74951183993';

// Глобальные переменные
let callId = null;
let conversationalAIClient = undefined;
let call = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
let isReconnecting = false;
let reconnectTimer = null;

/**
 * Основная функция
 */
function main() {
    try {
        callId = `call_${Date.now()}`;
        Logger.write(`📞 Устойчивый сценарий ElevenLabs: ${callId}`);
        
        setTimeout(function() {
            const customData = VoxEngine.customData();
            if (customData) {
                try {
                    const customDataParsed = JSON.parse(customData);
                    callId = customDataParsed.call_id || callId;
                    Logger.write(`📋 Custom data: ${JSON.stringify(customDataParsed)}`);
                } catch (e) {
                    Logger.write('Ошибка парсинга custom data: ' + e.message);
                }
            }
            
            setTimeout(function() {
                initiateCall();
            }, 1000);
        }, 100);
        
    } catch (error) {
        Logger.write('Ошибка в main(): ' + error.message);
        endScenario();
    }
}

/**
 * Инициация звонка
 */
function initiateCall() {
    try {
        const customData = VoxEngine.customData();
        let customDataParsed = {};
        
        if (customData) {
            try {
                customDataParsed = JSON.parse(customData);
            } catch (e) {
                Logger.write('Ошибка парсинга custom data: ' + e.message);
            }
        }
        
        const clientPhoneNumber = customDataParsed.phone || customDataParsed.phone_number;
        
        if (!clientPhoneNumber) {
            Logger.write('❌ Номер клиента не указан');
            endScenario();
            return;
        }
        
        Logger.write(`📞 Звоним на: ${clientPhoneNumber}`);
        
        call = VoxEngine.callPSTN(clientPhoneNumber, CALLER_ID);
        
        if (call) {
            call.addEventListener(CallEvents.Connected, async function(event) {
                Logger.write('📞 Звонок подключен!');
                
                // Отвечаем на звонок
                call.answer();
                
                // Настраиваем ElevenLabs после подключения
                await setupElevenLabs();
            });
            
            call.addEventListener(CallEvents.Disconnected, function(event) {
                Logger.write('📞 Звонок завершен пользователем');
                cleanupAndEnd();
            });
            
            call.addEventListener(CallEvents.Failed, function(event) {
                Logger.write('❌ Звонок не удался: ' + (event.reason || 'Неизвестная ошибка'));
                cleanupAndEnd();
            });
        }
        
    } catch (error) {
        Logger.write('Ошибка инициации звонка: ' + error.message);
        endScenario();
    }
}

/**
 * Настройка ElevenLabs с официальным модулем
 */
async function setupElevenLabs() {
    try {
        if (isReconnecting) {
            Logger.write('🔄 Переподключение к ElevenLabs...');
        } else {
            Logger.write('🔌 Настройка ElevenLabs с официальным модулем');
        }
        
        const customData = VoxEngine.customData();
        let customDataParsed = {};
        
        if (customData) {
            try {
                customDataParsed = JSON.parse(customData);
            } catch (e) {
                Logger.write('Ошибка парсинга custom data: ' + e.message);
            }
        }
        
        const agentId = customDataParsed.elevenlabs_agent_id || ELEVENLABS_AGENT_ID;
        const apiKey = customDataParsed.elevenlabs_api_key;
        
        // Обработчик закрытия WebSocket с попыткой переподключения
        const onWebSocketClose = async (event) => {
            Logger.write('🔌 ElevenLabs WebSocket закрыт');
            Logger.write(JSON.stringify(event));
            
            // Проверяем, не в процессе ли уже переподключения
            if (isReconnecting) {
                Logger.write('🔄 Уже в процессе переподключения, пропускаем');
                return;
            }
            
            // Попытка переподключения
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS && call && call.state() === 'connected') {
                isReconnecting = true;
                reconnectAttempts++;
                Logger.write(`🔄 Попытка переподключения ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`);
                
                // Очищаем предыдущий таймер
                if (reconnectTimer) {
                    clearTimeout(reconnectTimer);
                }
                
                reconnectTimer = setTimeout(async () => {
                    try {
                        await setupElevenLabs();
                    } catch (error) {
                        Logger.write('Ошибка переподключения: ' + error.message);
                        isReconnecting = false;
                    }
                }, 3000); // Ждем 3 секунды перед переподключением
            } else {
                Logger.write('🔌 Максимальное количество попыток переподключения достигнуто');
                isReconnecting = false;
            }
        };
        
        // Параметры для ElevenLabs клиента
        const conversationalAIClientParameters = {
            xiApiKey: apiKey,
            agentId: agentId,
            onWebSocketClose,
        };
        
        // Создаем клиент ElevenLabs используя правильный синтаксис
        conversationalAIClient = await ElevenLabs.createConversationalAIClient(conversationalAIClientParameters);
        
        if (conversationalAIClient && call) {
            Logger.write('✅ ElevenLabs клиент создан');
            
            // Отправляем медиа между звонком и ElevenLabs
            VoxEngine.sendMediaBetween(call, conversationalAIClient);
            
            // Настраиваем обработчики событий
            conversationalAIClient.addEventListener(ElevenLabs.ConversationalAIEvents.ConversationInitiationMetadata, (event) => {
                Logger.write('🎭 ElevenLabs диалог инициализирован');
                Logger.write(JSON.stringify(event));
                reconnectAttempts = 0; // Сбрасываем счетчик при успешном подключении
                isReconnecting = false;
            });
            
            conversationalAIClient.addEventListener(ElevenLabs.ConversationalAIEvents.AgentResponse, (event) => {
                Logger.write('🤖 Получен ответ от агента');
                Logger.write(JSON.stringify(event));
            });
            
            conversationalAIClient.addEventListener(ElevenLabs.ConversationalAIEvents.UserTranscript, (event) => {
                Logger.write('🎤 Пользователь сказал');
                Logger.write(JSON.stringify(event));
            });
            
            conversationalAIClient.addEventListener(ElevenLabs.ConversationalAIEvents.Interruption, (event) => {
                Logger.write('🔇 Прерывание пользователя');
                Logger.write(JSON.stringify(event));
                if (conversationalAIClient) conversationalAIClient.clearMediaBuffer();
            });
            
            conversationalAIClient.addEventListener(ElevenLabs.ConversationalAIEvents.Ping, (event) => {
                Logger.write('🏓 Ping от ElevenLabs');
                Logger.write(JSON.stringify(event));
            });
            
            Logger.write('🎵 ElevenLabs настроен для прямого воспроизведения аудио');
            
        } else {
            throw new Error('Не удалось создать ElevenLabs клиент');
        }
        
    } catch (error) {
        Logger.write('Ошибка настройки ElevenLabs: ' + error.message);
        Logger.write(error);
        
        // Если это не попытка переподключения, завершаем сценарий
        if (reconnectAttempts === 0) {
            endScenario();
        } else {
            isReconnecting = false;
        }
    }
}

/**
 * Очистка ресурсов и завершение
 */
function cleanupAndEnd() {
    try {
        Logger.write('🧹 Очистка ресурсов');
        
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        
        if (conversationalAIClient) {
            conversationalAIClient.close();
        }
        
        if (call) {
            call.hangup();
        }
        
        VoxEngine.terminate();
        
    } catch (error) {
        Logger.write('Ошибка очистки: ' + error.message);
        VoxEngine.terminate();
    }
}

/**
 * Завершение сценария
 */
function endScenario() {
    try {
        Logger.write('📞 Завершение сценария');
        cleanupAndEnd();
        
    } catch (error) {
        Logger.write('Ошибка завершения: ' + error.message);
        VoxEngine.terminate();
    }
}

// Обработчики событий приложения
VoxEngine.addEventListener('Application.Started', function(event) {
    Logger.write('🚀 Приложение запущено');
    
    if (event && event.customData) {
        try {
            const customDataParsed = JSON.parse(event.customData);
            callId = customDataParsed.call_id || callId;
        } catch (e) {
            Logger.write('Ошибка парсинга custom data: ' + e.message);
        }
    }
});

// Запускаем
main();




