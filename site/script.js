// Для Yandex Cloud заменить на http://PUBLIC_VM_IP:8080
const API_URL = "http://127.0.0.1:8080";

const keyInput = document.querySelector("#key");
const valueInput = document.querySelector("#value");
const resultBlock = document.querySelector("#result");
const commandButtons = document.querySelectorAll("[data-command]");

function showResult(message) {
  if (resultBlock) {
    resultBlock.textContent = message;
  }
}

async function runCommand(command) {
  const key = keyInput.value.trim();
  const value = valueInput.value.trim();
  const payload = { command, key, value };

  showResult("Отправка команды...");

  try {
    const response = await fetch(`${API_URL}/command`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      showResult(`Ошибка: ${data.error || "неизвестная ошибка"}`);
      return;
    }

    showResult(`Команда: ${data.command}\nОтвет сервера: ${data.result}`);
  } catch (error) {
    showResult(
      "Не удалось обратиться к HTTP API.\n" +
        "Проверьте, что запущены src/server.py и src/api.py.\n\n" +
        `Подробности: ${error.message}`,
    );
  }
}

commandButtons.forEach((button) => {
  button.addEventListener("click", () => runCommand(button.dataset.command));
});
