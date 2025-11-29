(function() {
  const root = document.getElementById('deck-root');
  const session = window.__PRACTICE_SESSION;
  if (!session) {
    root.innerHTML = "Session data not loaded.";
    return;
  }

  const questions = session.questions || [];
  let idx = 0;
  let answers = [];

  function render() {
    root.innerHTML = "";
    const q = questions[idx];

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h3>${q.text}</h3>
      <div>Rating: <span id="rate-val">5</span></div>
      <input id="rate" type="range" min="1" max="10" value="5" />
      <div class="controls">
        <button id="prev">Prev</button>
        <button id="next">Next</button>
      </div>
      <div class="hint">Swipe left/right OR use buttons</div>
    `;
    root.appendChild(card);

    const rate = document.getElementById("rate");
    const rateVal = document.getElementById("rate-val");
    rate.oninput = () => (rateVal.textContent = rate.value);

    document.getElementById("next").onclick = next;
    document.getElementById("prev").onclick = prev;

    // Basic swipe support
    let startX = null;
    card.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
    });
    card.addEventListener("touchend", (e) => {
      const endX = e.changedTouches[0].clientX;
      if (startX - endX > 60) next();
      if (endX - startX > 60) prev();
    });
  }

  function prev() {
    if (idx === 0) return;
    idx--;
    render();
  }

  async function next() {
    const q = questions[idx];
    const v = Number(document.getElementById("rate").value);
    answers.push({ q_id: q.id, value: v });

    idx++;

    if (idx >= questions.length) {
      // Submit answers
      const payload = {
        user_id: null,
        date_local: new Date().toLocaleDateString("en-CA"),
        answers,
        session_id: session.session_id
      };

      const res = await fetch("/api/session/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      // Debug info: print full response in console
      console.log("session submit response:", data);

      // Replace alert with result panel
      root.innerHTML = `
        <div class="card">
          <h2>Result</h2>
          <div><strong>Dominant:</strong> ${data.dominant} ${data.emoji || ""}</div>
          <div style="margin-top:8px"><strong>Archetype distribution:</strong></div>
          <pre id="dist" style="white-space:pre-wrap; background:#f3f4f6; padding:8px; border-radius:8px;">${JSON.stringify(data.archetype_dist, null, 2)}</pre>
          <div style="margin-top:12px">
            <button id="goto-calendar">Open Calendar</button>
            <button id="new-session">New Session</button>
          </div>
        </div>
      `;

      // emoji drop animation
      const el = document.createElement("div");
      el.style.position = "fixed";
      el.style.top = "-100px";
      el.style.left = "50%";
      el.style.fontSize = "64px";
      el.style.transform = "translateX(-50%)";
      el.textContent = data.emoji || "✨";
      document.body.appendChild(el);
      el.animate(
        [
          { transform: "translate(-50%, -200px) scale(1.6)" },
          { transform: "translate(-50%, 300px) scale(1)" }
        ],
        { duration: 900, easing: "cubic-bezier(.2,.8,.2,1)" }
      );
      setTimeout(() => el.remove(), 1500);

      document.getElementById("new-session").onclick = () => location.reload();
      document.getElementById("goto-calendar").onclick = () => alert("Calendar TBD");

      return;
    }

    render();
  }

  render();
})();
