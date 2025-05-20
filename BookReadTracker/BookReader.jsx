import debounce from 'lodash.debounce';
import { useState,useEffect,useCallback } from 'react';
import axios from 'axios';
import Button from './Button';
const BookReader = () => {
    let api = axios.create({
        baseURL: "http://localhost:3000"
    });
    let [data,setData]=useState([])
    let [add,setAdd]=useState(false)
    let [flag,setFlag]=useState(false)
    let [user,setUser]=useState("")
    let [password,setPassword]=useState("")
    let [login,setLogin]=useState("")
     useEffect(() => {
       if (!flag){ 
        localStorage.removeItem('token')
        return;
       }
         let getData = async () => {
        let d = await api.get(`/books/${user}`);
      setData(d.data);
      };
       getData();
       }, [flag]);

    let handelChange1=async (index,field,value)=>{
        let updated=data.map((item,ind)=>{
          return ind===index?{...item,[field]:value}:item
        })
        if(field==="currentPage"){
            let newStatus=value==updated[index].totalPage?"Completed":"In Progress";
             updated[index].status = newStatus
        }
        setData(updated)
    }

    const debouncedHandleChange = useCallback(
           debounce(async (bookId, index, field, value) => {

           await api.put(`/updateBook/${bookId}?field=${field}&value=${value}`);
            if (field === "currentPage") {
                let totalPage = data[index].totalPage;
                let newStatus = value == totalPage ? "Completed" : "In Progress";
                      await api.put(`/updateStatus/${bookId}?field=status&value=${newStatus}`);
                 }
    }, 500), // ⏱ 500ms delay
    [] 
  );
  const handelChange = (bookId,index,field,value) => {
    debouncedHandleChange(bookId,index,field,value);
  };

    let handelSignUp=async ()=>{
        let url=new URLSearchParams();
        url.append("username",user)
        url.append("password",password)
        let d= await api.post("/register",url,{
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            }
        })
        if(d.data){
            alert("User Created")
            setFlag(true)
            setLogin("")
        }else{
            setUser("")
            setPassword("")
        }
    }
    let getUser=async ()=>{
        let token = localStorage.getItem("token");
        let response = await api.get("/users/me/", {
            headers: { Authorization: `Bearer ${token}` }
        });

        if(response.data){
            setUser(response.data)
            setLogin("")
            setFlag(true)
        }
    }

    let handelLogin=async ()=>{
        let url=new URLSearchParams();
        url.append("username",user)
        url.append("password",password)
        let d= await api.post("/token",url,{
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            }
        })
          if (d.data.access_token) {
            localStorage.setItem("token", d.data.access_token);
            getUser();
        } else {
            alert("Invalid Credentials");
            setUser("");
            setPassword("");
            setLogin("");
        }
    }
    if(add){
        return <Button setAdd={setAdd} setData={setData} user={user}/>
    }
  if(flag){
  return (
    <div>
          <button onClick={(e)=>{setAdd(true)}}>Add Book</button>
          {data.map((item,index)=>{
            return (
                <div key={index}>
                    <h1>Title:- <span> {item.title} </span> </h1>
                    <h2>Author:- <span>  {item.author} </span></h2>
                    <h3> CurrentPage:- <span> <input type='range' value={item.currentPage} min={0} max={item.totalPage} onChange={(e)=>{
                        handelChange1(index,'currentPage',parseInt(e.target.value))
                        handelChange(item._id,index,'currentPage',parseInt(e.target.value))
                    }}/> {item.currentPage} </span></h3>
                    <h3> TotalPage:- <span> {item.totalPage} </span> </h3>
                    <h3>Status :- <span> {item.status} </span> </h3>
                    <h2>Current Progress :- {(item.currentPage*100)/item.totalPage}%</h2>
                    <button onClick={()=>{
                        api.delete(`/book/${item._id}`)
                        let temp=data.filter((ele,ind)=> ind!=index)
                        setData(temp)
                    }}>Delete </button>
                </div>
            )
          })}
    </div>
  )
  }
  if(login==="signup"){
    return (
        <div>
            <h1>SignUp</h1>
            <form method="post" onSubmit={(e) => {
                e.preventDefault();
                handelSignUp()
            }}>
            <input type="text" name="username" placeholder="Enter Username" onChange={(e)=>{
                    setUser(e.target.value)
                }}/>
                <input type="password" name="password" placeholder="Enter Password" onChange={(e)=>{
                    setPassword(e.target.value)
                }}/>
             <input type="submit"/>
            </form>
        </div>
    )
  }else if(login==="login"){
    return (
        <div>
            <h1>Login</h1>
            <form method="post" onSubmit={(e) => {
                e.preventDefault();
                handelLogin();
            }}> 
           <input type="text" name="username" placeholder="Enter Username" onChange={(e)=>{
                    setUser(e.target.value)
                }}/>
                <input type="password" name="password" placeholder="Enter Password" onChange={(e)=>{
                    setPassword(e.target.value)
                }}/>
                <input type="submit"/>
            </form>
        </div>
    )
  }
  return (
    <div>
         <button onClick={()=>{
           setLogin("login")
         }}> Login </button>
         <button onClick={()=>{
            setLogin("signup")
         }}
         > SignUp </button>
    </div>
  )
}

export default BookReader
