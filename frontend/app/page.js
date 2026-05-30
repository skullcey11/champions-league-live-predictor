"use client";

import { useEffect, useMemo, useState } from "react";

export default function Home() {
  const [mode, setMode] = useState("live");
  const [prediction, setPrediction] = useState(null);
  const [liveStatus, setLiveStatus] = useState("");
  const [motm, setMotm] = useState([]);

  const [recentForm, setRecentForm] = useState({
    psg: [],
    arsenal: [],
  });

  const [form, setForm] = useState({
    minute: 0,
    added_time: 0,

    psg_goals: 0,
    arsenal_goals: 0,

    psg_shots: 0,
    arsenal_shots: 0,

    psg_corners: 0,
    arsenal_corners: 0,

    psg_possession: 50,
    arsenal_possession: 50,
  });

  const isLiveMode = mode === "live";

  const totalMatchMinute = useMemo(() => {
    return (
      Number(form.minute) +
      Number(form.added_time)
    );
  }, [form]);

  useEffect(() => {
    if (!isLiveMode) return;

    fetchLiveMatch();
    fetchRecentForm();

    const interval = setInterval(() => {
      fetchLiveMatch();
      fetchRecentForm();
    }, 30000);

    return () => clearInterval(interval);
  }, [isLiveMode]);

  const fetchRecentForm = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/recent-form"
      );
      const data = await res.json();
      setRecentForm(data);
    } catch (err) {
      console.log(err);
    }
  };

  const fetchMOTM = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/motm"
      );

      const data = await res.json();
      setMotm(data);
    } catch (err) {
      console.log(err);
    }
  };

  const runPrediction = async (
    payloadOverride = null
  ) => {
    const payload =
      payloadOverride || {
        ...form,
        minute: totalMatchMinute,
      };

    const res = await fetch(
      "http://127.0.0.1:8000/predict",
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    const data = await res.json();
    setPrediction(data);
  };

  const fetchLiveMatch = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/live-match"
      );

      const data = await res.json();

      setLiveStatus(
        data.status || ""
      );

      const updatedForm = {
        ...form,
        minute:
          data.minute ?? 0,
        added_time:
          data.added_time ?? 0,

        psg_goals:
          data.psg_goals ?? 0,

        arsenal_goals:
          data.arsenal_goals ?? 0,

        psg_shots:
          data.psg_shots ?? 0,

        arsenal_shots:
          data.arsenal_shots ?? 0,

        psg_corners:
          data.psg_corners ?? 0,

        arsenal_corners:
          data.arsenal_corners ?? 0,

        psg_possession:
          data.psg_possession ??
          50,

        arsenal_possession:
          data.arsenal_possession ??
          50,
      };

      setForm(updatedForm);

      await fetchMOTM();

      if (isLiveMode) {
        await runPrediction({
          ...updatedForm,
          minute:
            Number(
              updatedForm.minute
            ) +
            Number(
              updatedForm.added_time
            ),
        });
      }
    } catch (err) {
      console.log(err);
    }
  };

  const increment = (
    field,
    max = 20
  ) => {
    if (isLiveMode) return;

    setForm((prev) => ({
      ...prev,
      [field]: Math.min(
        prev[field] + 1,
        max
      ),
    }));
  };

  const decrement = (field) => {
    if (isLiveMode) return;

    setForm((prev) => ({
      ...prev,
      [field]: Math.max(
        prev[field] - 1,
        0
      ),
    }));
  };

  const updatePossession = (
    value
  ) => {
    if (isLiveMode) return;

    const psg =
      Number(value);

    setForm((prev) => ({
      ...prev,
      psg_possession:
        psg,
      arsenal_possession:
        100 - psg,
    }));
  };

  const resultColor = (
    result
  ) => {
    if (result === "W")
      return "bg-green-500";
    if (result === "D")
      return "bg-yellow-500";
    return "bg-red-500";
  };

  const Counter = ({
    label,
    field,
    value,
    max = 20,
  }) => (
    <div className="mb-5">
      <label className="block mb-2">
        {label}
      </label>

      <div className="flex items-center gap-4">
        <button
          disabled={isLiveMode}
          onClick={() =>
            decrement(field)
          }
          className="bg-zinc-700 w-10 h-10 rounded disabled:opacity-40"
        >
          −
        </button>

        <div className="w-12 text-center text-xl font-bold">
          {value}
        </div>

        <button
          disabled={isLiveMode}
          onClick={() =>
            increment(
              field,
              max
            )
          }
          className="bg-zinc-700 w-10 h-10 rounded disabled:opacity-40"
        >
          +
        </button>
      </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">

        <div className="flex justify-center items-center gap-8 mb-8">
          <img
            src="https://a.espncdn.com/i/teamlogos/soccer/500/160.png"
            className="w-16 h-16"
            alt="PSG"
          />

          <h1 className="text-4xl font-bold">
            PSG vs Arsenal Live Predictor
          </h1>

          <img
            src="https://a.espncdn.com/i/teamlogos/soccer/500/359.png"
            className="w-16 h-16"
            alt="Arsenal"
          />
        </div>

        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() =>
              setMode("live")
            }
            className={`px-6 py-3 rounded-lg font-semibold ${
              isLiveMode
                ? "bg-red-600"
                : "bg-zinc-800"
            }`}
          >
            🔴 Live Mode
          </button>

          <button
            onClick={() =>
              setMode("manual")
            }
            className={`px-6 py-3 rounded-lg font-semibold ${
              !isLiveMode
                ? "bg-green-600"
                : "bg-zinc-800"
            }`}
          >
            ⚽ Simulator Mode
          </button>
        </div>

        {liveStatus && (
          <div className="text-center mb-8">
            <span className="bg-zinc-800 px-5 py-2 rounded-full text-lg font-semibold">
              {liveStatus}
            </span>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-10">
          <div className="bg-zinc-900 p-6 rounded-xl">
            <h3 className="text-blue-400 font-bold mb-3">
              PSG Last 5
            </h3>

            <div className="flex gap-2">
              {recentForm.psg.map(
                (result, i) => (
                  <div
                    key={i}
                    className={`${resultColor(result)} w-10 h-10 rounded-full flex items-center justify-center font-bold`}
                  >
                    {result}
                  </div>
                )
              )}
            </div>
          </div>

          <div className="bg-zinc-900 p-6 rounded-xl">
            <h3 className="text-red-400 font-bold mb-3">
              Arsenal Last 5
            </h3>

            <div className="flex gap-2">
              {recentForm.arsenal.map(
                (result, i) => (
                  <div
                    key={i}
                    className={`${resultColor(result)} w-10 h-10 rounded-full flex items-center justify-center font-bold`}
                  >
                    {result}
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">

          <div className="bg-zinc-900 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-6">
              Match Info
            </h2>

            <Counter
              label="Minute"
              field="minute"
              value={form.minute}
              max={120}
            />

            <Counter
              label="Added Time"
              field="added_time"
              value={form.added_time}
              max={15}
            />
          </div>

          <div className="bg-zinc-900 rounded-xl p-6">
            <h2 className="text-xl font-bold text-blue-400 mb-6">
              PSG Stats
            </h2>

            <Counter label="Goals" field="psg_goals" value={form.psg_goals} max={10} />
            <Counter label="Shots" field="psg_shots" value={form.psg_shots} max={30} />
            <Counter label="Corners" field="psg_corners" value={form.psg_corners} max={20} />
          </div>

          <div className="bg-zinc-900 rounded-xl p-6">
            <h2 className="text-xl font-bold text-red-400 mb-6">
              Arsenal Stats
            </h2>

            <Counter label="Goals" field="arsenal_goals" value={form.arsenal_goals} max={10} />
            <Counter label="Shots" field="arsenal_shots" value={form.arsenal_shots} max={30} />
            <Counter label="Corners" field="arsenal_corners" value={form.arsenal_corners} max={20} />
          </div>
        </div>

        <div className="mt-8">
          <label>
            PSG Possession:
            {form.psg_possession}%
          </label>

          <input
            type="range"
            min="0"
            max="100"
            disabled={isLiveMode}
            value={form.psg_possession}
            onChange={(e) =>
              updatePossession(
                e.target.value
              )
            }
            className="w-full mt-2"
          />

          <div className="mt-2">
            Arsenal:
            {
              form.arsenal_possession
            }
            %
          </div>
        </div>

        {!isLiveMode && (
          <button
            onClick={() =>
              runPrediction()
            }
            className="mt-8 w-full bg-green-600 rounded p-4 text-xl font-semibold"
          >
            Predict Match Outcome
          </button>
        )}

        {prediction && (
          <div className="mt-10 bg-zinc-900 rounded-xl p-8">
            <h2 className="text-3xl font-bold text-center mb-6">
              Prediction
            </h2>

            {[
              ["PSG Win", prediction.psg_win, "bg-blue-500"],
              ["Draw", prediction.draw, "bg-gray-400"],
              ["Arsenal Win", prediction.arsenal_win, "bg-red-500"],
            ].map(([label, value, color]) => (
              <div key={label} className="mb-5">
                <div className="flex justify-between mb-2">
                  <span>{label}</span>
                  <span>{value}%</span>
                </div>

                <div className="w-full bg-zinc-700 rounded-full h-4">
                  <div
                    className={`${color} h-4 rounded-full`}
                    style={{
                      width: `${value}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {motm.length > 0 && (
          <div className="mt-10 bg-zinc-900 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-center mb-6">
              ⭐ Man of the Match Predictor
            </h2>

            <div className="space-y-5">
              {motm.map(
                (
                  player,
                  index
                ) => (
                  <div
                    key={
                      player.name
                    }
                  >
                    <div className="flex justify-between mb-2">
                      <span>
                        #{index + 1} {player.name}
                      </span>

                      <span>
                        {player.score}%
                      </span>
                    </div>

                    <div className="w-full bg-zinc-700 rounded-full h-4">
                      <div
                        className="bg-yellow-400 h-4 rounded-full"
                        style={{
                          width: `${player.score}%`,
                        }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}