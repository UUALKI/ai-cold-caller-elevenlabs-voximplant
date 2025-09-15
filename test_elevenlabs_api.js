const axios = require('axios');

const API_KEY = 'sk_ff39c1d16620e8788133b568029a26401b92f1918cd89f40';
const AGENT_ID = 'agent_01jxd1arjvfq9bd1ae6j92cs3t';

async function testElevenLabsAPI() {
    console.log('🔍 Тестирование ElevenLabs Agent API...\n');
    console.log(`🔑 API Key: ${API_KEY.substring(0, 20)}...`);
    console.log(`🤖 Agent ID: ${AGENT_ID}\n`);
    
    // Тест 1: Проверка API ключа через /voices endpoint
    console.log('1️⃣ Тест API ключа через /voices endpoint...');
    try {
        const voicesResponse = await axios.get('https://api.elevenlabs.io/v1/voices', {
            headers: {
                'xi-api-key': API_KEY
            }
        });
        console.log('✅ API ключ работает! Доступно голосов:', voicesResponse.data.voices?.length || 0);
    } catch (error) {
        console.log('❌ Ошибка API ключа:', error.response?.status, error.response?.data);
    }
    
    // Тест 2: Получение списка агентов
    console.log('\n2️⃣ Получение списка агентов...');
    try {
        const agentsResponse = await axios.get('https://api.elevenlabs.io/v1/agent', {
            headers: {
                'xi-api-key': API_KEY
            }
        });
        console.log('✅ Агенты получены:', agentsResponse.data.agents?.length || 0);
        if (agentsResponse.data.agents) {
            agentsResponse.data.agents.forEach((agent, index) => {
                console.log(`   ${index + 1}. ${agent.name} (${agent.agent_id}) - ${agent.status}`);
            });
        }
    } catch (error) {
        console.log('❌ Ошибка получения агентов:', error.response?.status, error.response?.data);
        console.log('   Полный ответ:', error.response?.data);
    }
    
    // Тест 3: Проверка конкретного агента
    console.log('\n3️⃣ Проверка конкретного агента...');
    try {
        const agentResponse = await axios.get(`https://api.elevenlabs.io/v1/agent/${AGENT_ID}`, {
            headers: {
                'xi-api-key': API_KEY
            }
        });
        console.log('✅ Агент найден:', agentResponse.data.name);
        console.log('   ID:', agentResponse.data.agent_id);
        console.log('   Статус:', agentResponse.data.status);
        console.log('   Тип:', agentResponse.data.agent_type);
        console.log('   Описание:', agentResponse.data.description || 'Нет описания');
    } catch (error) {
        console.log('❌ Агент не найден:', error.response?.status, error.response?.data);
        console.log('   Полный ответ:', error.response?.data);
    }
    
    // Тест 4: Проверка пользователя
    console.log('\n4️⃣ Проверка пользователя...');
    try {
        const userResponse = await axios.get('https://api.elevenlabs.io/v1/user', {
            headers: {
                'xi-api-key': API_KEY
            }
        });
        console.log('✅ Пользователь:', userResponse.data.first_name, userResponse.data.last_name);
        console.log('   Email:', userResponse.data.email);
        console.log('   Subscription:', userResponse.data.subscription?.tier);
        console.log('   Character Count:', userResponse.data.subscription?.character_count);
        console.log('   Character Limit:', userResponse.data.subscription?.character_limit);
    } catch (error) {
        console.log('❌ Ошибка получения данных пользователя:', error.response?.status, error.response?.data);
    }
    
    // Тест 5: Тест диалога с агентом
    console.log('\n5️⃣ Тест диалога с агентом...');
    try {
        const conversationResponse = await axios.post(`https://api.elevenlabs.io/v1/agent/${AGENT_ID}/conversation`, {
            session_id: `test_session_${Date.now()}`,
            message_type: "greeting",
            message: "",
            voice_id: "21m00Tcm4TlvDq8ikWAM"
        }, {
            headers: {
                'xi-api-key': API_KEY,
                'Content-Type': 'application/json'
            }
        });
        console.log('✅ Диалог с агентом работает!');
        console.log('   Ответ:', conversationResponse.data.response || conversationResponse.data.message);
    } catch (error) {
        console.log('❌ Ошибка диалога с агентом:', error.response?.status, error.response?.data);
        console.log('   Полный ответ:', error.response?.data);
    }
}

testElevenLabsAPI().catch(console.error);
