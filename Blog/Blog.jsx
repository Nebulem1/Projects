import { useEffect, useState } from "react"
import Button from "./Button";
import axios from "axios";
const Blog = () => {
    let api = axios.create({
        baseURL: "http://localhost:3000"
    });

    const [blogs,setBlogs]=useState([])
    const [filtered,setFiltered]=useState([])
    
    //Variables
    const [user,setUser]=useState("")
    const [password,setPassword]=useState("")
    const [log,setLog]=useState("")
    const [view,setView]=useState("home")
    const [showButtons, setShowButtons] = useState(true);
    const [search,setSearch]=useState("")

    //functions
    const checkOwner=(index)=>{
      
        return blogs[index].username===user
    }
   
    let searchData=(item)=>{
        let update=blogs.filter( (ele)=>{
          return ele.title.toLowerCase().includes(item.toLowerCase())
        })
        setFiltered(update)
    }

    let getToken = async (user, password) => {
        let token = await api.post("/token",{"username":user,"password":password})
       
        localStorage.setItem("token", token.data.token_access);
    }
    let getData= async (token)=>{
        let d= await api.get("/users/me/", {
            headers: {"Authorization": `Bearer ${token}`}
          });
        return d
     }
    const handelChange=(index,key,data)=>{
         const updated=blogs.map((ele,i)=>{
            return i==index?{...ele,[key]:data}:ele;
         })
          setBlogs(updated)
    }
    const handleDelete = async (id) => {
      try {
        await api.delete(`/delete/${id}`);
        setBlogs(prev => prev.filter((ele) => ele._id !== id));
        setFiltered(prev => prev.filter((ele) => ele._id !== id));
      } catch (err) {
        console.error("Failed to delete:", err.response?.data || err.message);
      }
    };

    //Loading Data
    useEffect(()=>{
        const fetchData = async () => {
            try {
              const app = await api.get("/getData");
           
              setBlogs(app.data);
              setFiltered(app.data)
              console.log(app.data);
            } catch (error) {
              console.error("Error fetching data:", error);
            }
          };
        
          fetchData();
    },[])
    //Main logic
    if(view==='add'){
       return <Button  user={user} setBlogs={setBlogs} setView={setView} setFiltered={setFiltered}/>
    }
    if(log==='login'){
        return <div>
        <input type="text" onChange={(e)=>{setUser(e.target.value)}} value={user}/>
        <input type="password" onChange={(e)=>{setPassword(e.target.value)}} value={password}/>
         <button onClick={async ()=>{
           await getToken(user,password);
           let msg=await getData(localStorage.getItem('token'))
           if(msg){
            setShowButtons(false)
            setLog("")
           }
         }}>Log In</button>
         <button onClick={()=>{
             setUser("")
             setLog('signup')                
         }}>SignUp</button>
      </div>

    }else if(log==='signup'){
        return <div> 
        <h1>Create User</h1>
        Enter UserName:-
        <input type="text" onChange={(e)=>{setUser(e.target.value)}} value={user}/>
        Enter Password:-
        <input type="password" onChange={(e)=>{setPassword(e.target.value)}} value={password}/>
         <button onClick={async ()=>{
           await api.post("/register",{"username":user,"password":password})
           setShowButtons(false)
           setLog('');
         }}>SignUp</button>        
        </div>
    }
    return (
    <div>
        <nav>
        {showButtons && (
            <>
            <button onClick={() =>{setLog('login') 
            searchData("")
            }}>LogIN</button>
            <button onClick={() =>{setLog('signup') 
              searchData("")
            }}>SignUP</button>
            </>
          )}

        </nav>
        <button onClick={()=>{
          api.post("/hand")
        }}>Hand Control</button>
        <section className="searchbar">
          <input type="text" value={search} onChange={(e)=>{setSearch(e.target.value) 
        }}/>      
          <button onClick={()=>{searchData(search)}}> Search</button>
        </section>
        <section>
        {user && (
            <button onClick={() => {
              setView("add")}
            }>Add Blog</button>
            
        )}
         {user && (
            <button onClick={()=>{
                setUser("")
                setShowButtons(true)
            }}>Logout</button>
         )}
       
        </section>
        <main className="Blogs">
          {
            filtered.map((ele,index)=>{
                return <div key={ele._id}>
                    <section> Title:- <span contentEditable={checkOwner(index)} onBlur={(e)=>{
                        handelChange(index,'title',e.target.textContent)
                    }}> {ele.title} </span> </section>
                    <section>Content:- <span  contentEditable={checkOwner(index)} onBlur={(e)=>{
                        handelChange(index,'content',e.target.textContent)
                    }} >  {ele.content} </span></section>
                    {checkOwner(index) && (
                       <button onClick={()=>{
                         handleDelete(ele._id)
                      }}>Delete</button>
                    )}
                </div>
            })
          }       
        </main>
    </div>
  )
}

export default Blog
