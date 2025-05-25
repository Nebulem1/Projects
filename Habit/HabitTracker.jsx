import debounce from "lodash.debounce";
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
const HabitTracker = () => {
  let api = axios.create({
    baseURL: "http://localhost:3000",
  });
  //Variables
  let [data, setData] = useState([]);
  let [progress, setProgress] = useState([]);
  let [user, setUser] = useState("");
  let [flag, setFlag] = useState(false);
  let [habit, setHabit] = useState("");
  let [category, setCategory] = useState("");
  let [frequency, setFrequency] = useState("");
  let [target_per_day, setTarget_per_day] = useState(0);
  let [password, setPassword] = useState("");
  let [log, setLog] = useState("");

  useEffect(() => {
    if (!flag) {
      localStorage.removeItem("token");
      return;
    }
    let getData = async () => {
      let d = await api.get(`/habits/${user}`);
      setData(d.data.habit);
      setProgress(d.data.progress);
    };
    getData();
  }, [flag]);

  //functions
  let handelChange1 = async (index, field, value, id) => {
    let updated = progress.map((item, ind) => {
      return ind === index ? { ...item, [field]: value } : item;
    });
    setProgress(updated);
  };
  let handelAnalatics = async (index, id, user, amount) => {
    let obj = {
      habit_id: id,
      user: user,
      date: new Date().toISOString().split("T")[0],
    };
    let streakData = await api.post("/analyse", obj);

    setProgress((prev) =>
      prev.map((item, ind) => {
        if (ind === index) {
          return {
            ...item,
            streak: streakData.data.current_streak,
            longest_streak: streakData.data.longest_streak,
            status: "completed",
            amount_done: amount,
          };
        }
        return item;
      })
    );
  };
  let handelSubmit = async () => {
    let ob = {
      name: habit,
      category: category,
      frequency: frequency,
      target_per_day: target_per_day,
      start_date: new Date().toISOString().split("T")[0],
      user: user,
    };
    let d = await api.post("/create_habit", ob);
    let progress = {
      habit_id: d.data._id,
      last_completed_date: new Date().toISOString().split("T")[0],
      amount_done: 0,
      status: "incomplete",
      streak: 0,
      longest_streak: 0,
      user: user,
    };
    await api.post("/progress", progress);
    setProgress((prev) => [...prev, progress]);
    setData((prev) => [...prev, d.data]);
  };

  let getUser = async () => {
    let token = localStorage.getItem("token");
    let response = await api.get("/users/me/", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.data) {
      console.log(response.data);
      setUser(response.data);
      setLog("");
      setFlag(true);
    }
  };

  let handelLogin = async () => {
    let url = new URLSearchParams();
    url.append("username", user);
    url.append("password", password);
    let d = await api.post("/token", url, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    if (d.data.access_token) {
      localStorage.setItem("token", d.data.access_token);
      getUser();
    } else {
      alert("Invalid Credentials");
      setUser("");
      setPassword("");
      setLog("");
    }
  };

  let handelSignUp = async () => {
    let url = new URLSearchParams();
    url.append("username", user);
    url.append("password", password);
    let d = await api.post("/register", url, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    if (d.data) {
      alert("User Created");
      setFlag(true);
      setLog("");
    } else {
      setUser("");
      setPassword("");
    }
  };
  let debouncedHandleChange = useCallback(
    debounce(async (Id, status, amount, user) => {
      let updateProgress = {
        habit_id: Id,
        date: new Date().toISOString().split("T")[0],
        status: status,
        amount_done: amount,
        user: user,
      };
      await api.put("/update_habit", updateProgress);
    }, 500),
    []
  );

  const updateApi = (Id, status, amount, user) => {
    debouncedHandleChange(Id, status, amount, user);
  };
  if (log == "login") {
    return (
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handelLogin();
        }}
      >
        Username
        <input
          type="text"
          placeholder="Enter User"
          onChange={(e) => {
            setUser(e.target.value);
          }}
        />
        password
        <input
          type="password"
          placeholder="Enter Password"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
        <input type="submit" />
      </form>
    );
  } else if (log == "signup") {
    return (
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handelSignUp();
        }}
      >
        Username
        <input
          type="text"
          placeholder="Enter User"
          onChange={(e) => {
            setUser(e.target.value);
          }}
        />
        password
        <input
          type="password"
          placeholder="Enter Password"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
        <input type="submit" />
      </form>
    );
  }
  if (flag) {
    return (
      <div>
        <h1>Habit Tracker</h1>
        {user && (
          <div>
            <label htmlFor="habit">Habit Name</label>
            <input
              type="text"
              id="habit"
              onChange={(e) => {
                setHabit(e.target.value);
              }}
            />
            <label htmlFor="category">Category</label>
            <input
              type="text"
              id="category"
              onChange={(e) => {
                setCategory(e.target.value);
              }}
            />
            <label htmlFor="frquency">Frequency</label>
            Daily
            <input
              type="radio"
              id="frequency"
              value="daily"
              name="freq"
              onChange={(e) => {
                setFrequency(e.target.value);
              }}
            />
            Weekly
            <input
              type="radio"
              id="frequency"
              value="weekly"
              name="freq"
              onChange={(e) => {
                setFrequency(e.target.value);
              }}
            />
            monthly
            <input
              type="radio"
              id="frequency"
              value="monthly"
              name="freq"
              onChange={(e) => {
                setFrequency(e.target.value);
              }}
            />
            <label htmlFor="target_per_day">Target per day</label>
            <input
              type="number"
              id="target_per_day"
              onChange={(e) => {
                setTarget_per_day(e.target.value);
              }}
            />
            <button
              type="button"
              onClick={() => {
                handelSubmit();
              }}
            >
              Add Habit
            </button>
          </div>
        )}
        {data.map((item, index) => {
          return (
            <div key={item._id}>
              <h2>{item.name}</h2>
              <p>Category: {item.category}</p>
              <p>Frequency: {item.frequency}</p>
              <p>Target per day: {item.target_per_day}</p>
              <p>Start date: {item.start_date.split("T")[0]}</p>
              <h2>Progress</h2>
              <p> Status :{progress[index].status}</p>
              <p>
                Amount done:{" "}
                <input
                  type="number"
                  value={progress[index].amount_done}
                  onChange={(e) => {
                    const newValue = parseInt(e.target.value, 10);
                    if (isNaN(newValue) || newValue < 0) {
                      alert("Please enter a non-negative number.");
                      return;
                    }

                    if (newValue < progress[index].amount_done) {
                      alert("Can't undo progress.");
                      return;
                    }
                    if (newValue === item.target_per_day) {
                      handelAnalatics(
                        index,
                        progress[index].habit_id,
                        user,
                        newValue
                      );
                      updateApi(
                        progress[index].habit_id,
                        "completed",
                        newValue,
                        user
                      );
                    } else {
                      handelChange1(
                        index,
                        "amount_done",
                        newValue,
                        progress[index].habit_id
                      );
                      updateApi(
                        progress[index].habit_id,
                        "incomplete",
                        newValue,
                        user
                      );
                    }
                  }}
                />{" "}
              </p>
              <p>Current Streak :{progress[index].streak} </p>
              <p>Longest Streak :{progress[index].longest_streak} </p>
              <button
                onClick={async () => {
                  await api.delete(`/delete_habit/${item._id}`);
                  let temp = data.filter((ele, ind) => ind != index);
                  let temp1 = progress.filter((ele, ind) => ind != index);
                  setData(temp);
                  setProgress(temp1);
                }}
              >
                Delete{" "}
              </button>
            </div>
          );
        })}
      </div>
    );
  }
  return (
    <div>
      <h1>Habit Tracker</h1>
      <button
        onClick={(e) => {
          setLog("login");
          console.log(user);
        }}
      >
        Login
      </button>
      <button
        onClick={(e) => {
          setLog("signup");
        }}
      >
        SignUp
      </button>
    </div>
  );
};

export default HabitTracker;