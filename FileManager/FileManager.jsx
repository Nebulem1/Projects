import axios from "axios"
import { useState,useEffect } from "react";

const FileManager = () => {
    let api = axios.create({
        baseURL: "http://localhost:3000"
    });
 
    let [data,setData]=useState([])
   //variables
   let [title,setTitle]=useState("")
   let [category,setCategory]=useState("")
   let [file,setFile]=useState(null)
   let [user,setUser]=useState("")
   let [password,setPassword]=useState("")
    let [log,setLog]=useState("")

   useEffect(()=>{
    let getData=async ()=>{
        let d= await api.get("/files")
        setData(d.data)
    }
    getData()
   }
   ,[])
  
   //functions

    let handelSort=(updatedData)=>{       
    let low = 0;
    let mid = 0;
    let high = updatedData.length - 1;
    while (mid <= high) {
      if (updatedData[mid].category === 'personal') {
        [updatedData[low], updatedData[mid]] = [updatedData[mid], updatedData[low]];
        low++;
        mid++;
      } else if (updatedData[mid].category === 'college') {
        [updatedData[mid], updatedData[high]] = [updatedData[high], updatedData[mid]];
        high--;
      } else {
        mid++;
      }
     }
    } 

   let handleSubmit=async ()=>{
   let form=new FormData()
    form.append("file",file)
    form.append("title",title)
    form.append("category",category)
    form.append("owner",user)
    let d= await api.post("/uploadfile",form,{
        headers:{
            "Content-Type":"multipart/form-data"
        }
    })
    let updated=[...data,d.data]
    handelSort(updated)
    setData(updated)
}

    let handelDownload=async (id,filename)=>{
        let response =await api.get(`/download/${id}`,{responseType:"blob"})
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename); 
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);        
    }

    let checkOwner=(owner)=>{
        return owner===user
    }

   const handelChange=(index,key,value)=>{
         const updated=data.map((ele,i)=>{
            return i==index?{...ele,[key]:value}:ele;
         })
          setData(updated)
    }

   const getToken = async (user, password) => {
        let url = new URLSearchParams();
        url.append("username", user);
        url.append("password", password);

        const response = await api.post("/token", url, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        if (response.data.access_token) {
            localStorage.setItem("token", response.data.access_token);
            getUser();
        } else {
            
            alert("Invalid Credentials");
            setUser("");
            setPassword("");
            setLog("");
        }
    }
     
const getUser = async () => {
    try {
        let token = localStorage.getItem("token");
        console.log(token)
        let response = await api.get("/users/me/", {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log("Logged in as:", response.data);
    } catch (error) {
        localStorage.removeItem("token");
        setUser("");
        setPassword("");
    }
};
    if(log==="login"){
        return (
            <form method="post" onSubmit={(e) => {
                e.preventDefault();
                getToken(user,password)
                setLog("")
            }}>
                <input type="text" name="username" placeholder="Enter Username" onChange={(e)=>{
                    setUser(e.target.value)
                }}/>
                <input type="password" name="password" placeholder="Enter Password" onChange={(e)=>{
                    setPassword(e.target.value)
                }}/>
                <input type="submit"/>
            </form>
        )
    }
    else if(log==="signup"){
        return (
            <form action="" method="post" onSubmit={async (e) => {
                e.preventDefault();
                let url= new URLSearchParams()
                url.append("username",user)
                url.append("password",password)
                await api.post("/register",url,{
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                })
                setLog("login")
            }}>
                <input type="text" name="username" placeholder="Enter Username" onChange={(e)=>{
                    setUser(e.target.value)
                }}/>
                <input type="password" name="password" placeholder="Enter Password" onChange={(e)=>{
                    setPassword(e.target.value)
                }}/>
                <input type="submit"/>
            </form>
        )
    }
   return (
    <div>
        {!user &&(
            <div> 
             <button onClick={()=>{setLog("login")}}>Login</button>
         <button onClick={()=>{
            setLog("signup")
         }} >SignUp</button>
         </div>
        )}


         {user && (
            <div>  
                <button onClick={()=>{
                    setUser("")
                }}>LogOut</button>
         <form  method="post" onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
          }}>
            <input type="file" name="file" onChange={(e)=>{
                setFile(e.target.files[0])
            }}/>
            <input type="text" name="title" placeholder="Enter Title" onChange={(e)=>{
                setTitle(e.target.value)
            }}/>
             Personal
            <input type="radio" name="category" value="personal" onClick={(e)=>{setCategory(e.target.value)}} />
            College
            <input type="radio" name="category" value="college" onClick={(e)=>{setCategory(e.target.value)}} />
            office
            <input type="radio" name="category" value="office" onClick={(e)=>{setCategory(e.target.value)}} />
            <input type="submit" value="Upload"/>
            </form>   
             </div>
             )}
            <section>
            <button onClick={async ()=>{
                await api.get("/hand")
            }}>Activate Hand Control</button>

            {data.map((item,index)=>{
               return <div key={item._id}>
                    <h3 contentEditable={checkOwner(item.owner)} onBlur={(e)=>{
                        handelChange(index,'title',e.target.textContent)
                    }} >{item.title}</h3>
                    college
                    <input type="radio" name={item._id} value="college" checked={item.category==='college'} disabled={!checkOwner(item.owner)} onClick={()=>{
                        handelChange(index,"category","college")
                    }}/>
                    personal
                    <input type="radio" name={item._id} value="personal" checked={item.category==='personal'} disabled={!checkOwner(item.owner)} onClick={()=>{
                        handelChange(index,"category","personal")
                    }}/>
                    office
                    <input type="radio" name={item._id} value="office" checked={item.category==='office'} disabled={!checkOwner(item.owner)} onClick={()=>{
                        handelChange(index,"category","office")
                    }}/>
                    <h3 contentEditable={checkOwner(item.owner)}  onBlur={(e)=>{
                        handelChange(index,'filename',e.target.textContent)
                    }} >{item.filename}</h3>
                    <button onClick={()=>{
                        handelDownload(item._id,item.filename)
                    }}>Download</button>

                    {checkOwner(item.owner) && (
                        <button onClick={()=>{
                            let temp=data.filter((ele,ind)=> ind!=index)
                            setData(temp)
                            api.delete(`/deletefile/${item._id}`)
                        }}>Delete</button>
                    )}
                </div>
            })
            }
            </section>    
    </div>
  )
}

export default FileManager