import axios from "axios";
import { useState } from "react"
const Button = ({user,setBlogs,setView ,setFiltered}) => {
    let api = axios.create({
     baseURL: "http://localhost:3000"
   });
       const [title,setTitle]=useState("")
      const [content,setContent]=useState("")
  return (
      
     <div>
        <input type="text" onChange={(e)=>{
          setTitle(e.target.value)
        }} />
        <textarea rows="5" cols="6" onChange={(e)=>{
           setContent(e.target.value)
        }}> </textarea>

        <button onClick={async ()=>{
           let d=await api.post("/setData", { 'title': title, 'content': content, 'username': user })
           let  data=d.data
          setBlogs(prev => [
            ...prev,
            data
          ]
        );
           setFiltered(prev=>[
            ...prev,
            data
           ])
           
        setView('home')
      
}}>Submit</button>
      </div>
  )
}

export default Button
