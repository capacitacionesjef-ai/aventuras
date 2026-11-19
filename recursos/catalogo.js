const filters = document.querySelector(".filters");
const buttons = Array.from(filters.querySelectorAll("button"));
const cards = Array.from(document.querySelectorAll(".card"));
const results = document.querySelector("#results");

for (const button of buttons) {
  button.addEventListener("click", () => {
    const selected = button.dataset.destino;
    for (const option of buttons) {
      option.setAttribute("aria-pressed", String(option === button));
    }
    for (const card of cards) {
      card.hidden = Boolean(selected) && card.dataset.destino !== selected;
    }
    const visible = cards.filter((card) => !card.hidden).length;
    results.textContent = visible === 1 ? "1 actividad" : `${visible} actividades`;
  });
}
filters.hidden = false;
