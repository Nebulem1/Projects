import axios from 'axios'
import {useState} from 'react'


const TaskManager = () => {
    let api = axios.create({
        baseURL: "http://localhost:3000"
    });

    let [data,setData]=useState([])
    let [completed,setCompleted]=useState([])
    
    let getToken = async (user, password) => {
        let token = await api.post("/token",{"username":user,"password":password})
        localStorage.setItem("token", token.data.access_token);
     }

     let getData= async (token)=>{
        let d= await api.get("/users/me/", {
            headers: {"Authorization": `Bearer ${token}`}
          });
        setData(d.data.Task)
        return true
     }
      //For Update one of best method
     const handleInputChange = (index, field, value) => {
        const updatedData = data.map((item, i) =>
          i === index ? { ...item, [field]: value } : item
        );
        setData(updatedData);
      };
      
    let handelSort=(updatedData)=>{       
    let low = 0;
    let mid = 0;
    let high = updatedData.length - 1;
    while (mid <= high) {
      if (updatedData[mid].status === 'Pending') {
        [updatedData[low], updatedData[mid]] = [updatedData[mid], updatedData[low]];
        low++;
        mid++;
      } else if (updatedData[mid].status === 'Completed') {
        [updatedData[mid], updatedData[high]] = [updatedData[high], updatedData[mid]];
        high--;
      } else {
        mid++;
      }
     }
    }
   
    let handelCompleted=(data)=>{
        let low=0;
        let high=data.length-1;
        while(low<=high){
            let mid= parseInt((low+high)/2);
            if(data[mid].status==='Completed'){
                high=mid-1;
            }else{
                low=mid+1;
            }
        }
        
        setCompleted(data.filter((ele,ind)=>{
            return ind>=low
        }))
         
    }

    let handelTasks =(title,description,status)=>{
        let ob={
            title:title,
            description:description,
            status:status
        }
        const updatedData = [...data, ob];
        handelSort(updatedData)
        handelCompleted(updatedData)
        setData(updatedData);
    }
   
    let [title,setTitle]=useState("")
    let [description,setDescription]=useState("")
    let [status,setStatus]=useState("")
    let[login,setLogin]=useState(true)
    const [user, setUser] = useState("");
    const[password, setPassword] = useState("");
     
    if(login===true){
          return <div>
            <input type="text" onChange={(e)=>{setUser(e.target.value)}} value={user}/>
            <input type="password" onChange={(e)=>{setPassword(e.target.value)}} value={password}/>
             <button onClick={async ()=>{
               await getToken(user,password);
               let msg=await getData(localStorage.getItem('token'))
               if(msg){
                setLogin("")
               }
             }}>Log In</button>
             <button onClick={()=>{
                 setLogin(false)                
             }}>SignUp</button>
          </div>
    }else if(login===false){
        return <div> 
        <h1>Create User</h1>
        Enter UserName:-
        <input type="text" onChange={(e)=>{setUser(e.target.value)}} value={user}/>
        Enter Password:-
        <input type="password" onChange={(e)=>{setPassword(e.target.value)}} value={password}/>
         <button onClick={async ()=>{
           await api.post("/register",{"username":user,"password":password})
           setLogin(true);
         }}>SignUp</button>        
        </div>
    }else{
    return (
    <div>
         <textarea rows={3} cols={10} onChange={(e)=>{
              setTitle(e.target.value)
         }} placeholder='Title'/>   
         
         <textarea rows={5} cols={10} onChange={(e)=>{
              setDescription(e.target.value)
         }} placeholder='Description'/> 

         <span> 
         Completed
         <input type="radio" name='status' value='Completed' onClick={(e)=>{
            setStatus(e.target.value)
         }} />
         </span>
          <span> 
           Pending
         <input type="radio" name='status' value='Pending' onClick={(e)=>{
            setStatus(e.target.value)
         }}/>
         </span>
         <span> 
            InProgress
         <input type="radio" name='status' value='In Progress' onClick={(e)=>{
            setStatus(e.target.value)
         }}/>
         </span>
         
         <button onClick={(e)=>{
        handelTasks(title,description,status);
       
         }}>Add Task</button>
         
         <h1>Manage Tasks</h1>
         {
            data.map((ele,index)=>{
                return <section key={index}>
                    <div>Task :-{index+1}</div>
                    
                    <div >Title :- <span contentEditable={true} onBlur={(e)=>{
                       handleInputChange(index,'title',e.target.textContent)
                    }} > {ele.title} </span></div>
                    
                    <div>Description :- <span contentEditable={true} onBlur={(e)=>{
                        handleInputChange(index,'description',e.target.textContent)
                    }}> {ele.description} </span> </div>

                    <div>Status :- 
                          <span>
                            Completed
                            <input type="radio" checked={ele.status==='Completed'} name={"status"+index} value='Completed' onChange={(e) => {
       handleInputChange(index,'status',e.target.value)
      }}/>
                          </span>
                          <span>
                            Pending
                            <input type="radio" checked={ele.status==='Pending'} name={"status"+index} value='Pending' onChange={(e) => {
       handleInputChange(index,'status',e.target.value)
      }}/>
                          </span>
                          <span>
                            InProgress
                            <input type="radio" checked={ele.status==='In Progress'} name={"status"+index} value='In Progress' onChange={(e) => {
          handleInputChange(index,'status',e.target.value)
      }}/>
                          </span>
                    </div>

                    <button onClick={()=>{
                        let temp=data.filter((ele,ind)=> ind!=index)
                        setData(temp)
                    }}> Delete </button>
                </section>
            })
         }

         {completed && 
          <div> 
          <h2>Completed Tasks</h2>
            {completed.map((ele,ind)=>{
            return <li key={ind+80}>{ele.title}</li>
           }) }
           </div>
         }
        
         <button onClick={async ()=>{
            await api.post('/setTask',{"username":user,"Task":data})
            setLogin(true)
         }}>LogOut</button>
    </div>
  )
}
}
export default TaskManager
