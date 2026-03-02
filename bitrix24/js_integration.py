"""
Интеграция с Bitrix24 через JS SDK
Для использования в Node.js окружении
"""

import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path

class Bitrix24JSIntegration:
    """
    Обертка для работы с Bitrix24 JS SDK из Python
    Требует установленного Node.js и @bitrix24/b24jssdk
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.node_script_path = Path(__file__).parent / "js_scripts"
        self.node_script_path.mkdir(exist_ok=True)
    
    def _run_node_script(self, script_name: str, params: Dict) -> Dict:
        """Выполнение Node.js скрипта"""
        script_path = self.node_script_path / f"{script_name}.js"
        
        # Передаем параметры через stdin
        params_json = json.dumps({
            "webhook_url": self.webhook_url,
            **params
        })
        
        result = subprocess.run(
            ["node", str(script_path)],
            input=params_json,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Node.js script error: {result.stderr}")
        
        return json.loads(result.stdout)
    
    def batch_request(self, commands: List[Dict]) -> Dict:
        """
        Выполнение batch запроса через JS SDK
        Автоматически разбивает на чанки по 50 команд
        """
        return self._run_node_script("batch_request", {"commands": commands})
    
    def get_all_leads(self, filter_params: Dict = None) -> List[Dict]:
        """
        Получение всех лидов с использованием CallListV3
        Автоматически обрабатывает пагинацию
        """
        return self._run_node_script("get_all_leads", {
            "filter": filter_params or {}
        })
    
    def stream_deals(self, filter_params: Dict = None):
        """
        Потоковое получение сделок через FetchListV3
        Для работы с большими объемами данных
        """
        return self._run_node_script("stream_deals", {
            "filter": filter_params or {}
        })

# Создание Node.js скриптов для интеграции
def setup_node_scripts():
    """Создание необходимых Node.js скриптов"""
    
    scripts_dir = Path(__file__).parent / "js_scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # package.json
    package_json = {
        "name": "bitrix24-js-integration",
        "version": "1.0.0",
        "type": "module",
        "dependencies": {
            "@bitrix24/b24jssdk": "latest"
        }
    }
    
    with open(scripts_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    # batch_request.js
    batch_script = """
import { initializeB24 } from '@bitrix24/b24jssdk';
import * as readline from 'readline';

async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false
    });

    let inputData = '';
    
    for await (const line of rl) {
        inputData += line;
    }
    
    const params = JSON.parse(inputData);
    
    const b24 = await initializeB24({
        webhookUrl: params.webhook_url
    });
    
    // Используем BatchByChunkV3 для автоматического разбиения на чанки
    const result = await b24.callBatchByChunkV3(params.commands);
    
    console.log(JSON.stringify(result));
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
"""
    
    with open(scripts_dir / "batch_request.js", "w") as f:
        f.write(batch_script)
    
    # get_all_leads.js
    leads_script = """
import { initializeB24 } from '@bitrix24/b24jssdk';
import * as readline from 'readline';

async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false
    });

    let inputData = '';
    
    for await (const line of rl) {
        inputData += line;
    }
    
    const params = JSON.parse(inputData);
    
    const b24 = await initializeB24({
        webhookUrl: params.webhook_url
    });
    
    // Используем CallListV3 для получения всех лидов
    const leads = await b24.callListV3('crm.lead.list', {
        filter: params.filter,
        select: ['*', 'UF_*']
    });
    
    console.log(JSON.stringify(leads));
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
"""
    
    with open(scripts_dir / "get_all_leads.js", "w") as f:
        f.write(leads_script)
    
    print("Node.js scripts created successfully!")
    print(f"Run 'npm install' in {scripts_dir}")

if __name__ == "__main__":
    setup_node_scripts()
