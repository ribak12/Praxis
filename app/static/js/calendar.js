(async function () {
  const root = document.getElementById("calendar");

  // current month/year
  const year = new Date().getFullYear();
  const month = new Date().getMonth() + 1;
  const todayDay = new Date().getDate();

  // request stamps — use null for anonymous sessions (your dev mode)
  const res = await fetch("/api/calendar/get", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: null,
      year: year,
      month: month
    })
  });

  const data = await res.json();

  // clear and build grid (use daysInMonth if you compute it later)
  const daysInMonth = 31;
  root.innerHTML = "";

  for (let i = 1; i <= daysInMonth; i++) {
    const div = document.createElement("div");
    div.className = "day-cell";
    div.dataset.day = i;

    const stamp = data.find(d => {
      try {
        return Number(d.date.split("-")[2]) === i;
      } catch (e) { return false; }
    });

    if (stamp) div.textContent = stamp.emoji;
    else div.textContent = "";

    root.appendChild(div);
  }

  // slap animation for today's tile if it has an emoji
  const todayCell = document.querySelector(`[data-day="${todayDay}"]`);
  if (todayCell && todayCell.textContent.trim() !== "") {
    const emoji = todayCell.textContent.trim();

    const rect = todayCell.getBoundingClientRect();
    const fall = document.createElement("div");
    fall.textContent = emoji;
    fall.style.position = "fixed";
    fall.style.top = "-150px";
    // position roughly above tile center
    fall.style.left = (rect.left + rect.width / 2) + "px";
    fall.style.transform = "translateX(-50%)";
    fall.style.fontSize = "64px";
    fall.style.pointerEvents = "none";
    fall.style.zIndex = 9999;
    document.body.appendChild(fall);

    // drop -> slap
    fall.animate(
      [
        { transform: "translate(-50%, -300px) scale(1.4)", opacity: 0.2 },
        { transform: "translate(-50%, 0px) scale(1)", opacity: 1 }
      ],
      { duration: 850, easing: "cubic-bezier(.3,.9,.2,1)" }
    );

    setTimeout(() => {
      todayCell.classList.add("glow");
      todayCell.animate(
        [
          { transform: "scale(1.18)" },
          { transform: "scale(0.96)" },
          { transform: "scale(1)" }
        ],
        { duration: 360, easing: "ease-out" }
      );
      fall.remove();
      // remove glow after a moment
      setTimeout(() => todayCell.classList.remove("glow"), 1200);
    }, 900);
  }
})();
