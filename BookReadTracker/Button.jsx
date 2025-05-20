import axios from "axios";
import { useState } from "react"
const Button = ({setAdd,setData,user}) => {
    let api = axios.create({
     baseURL: "http://localhost:3000"
   });
      
    let [title,setTitle]=useState("")
    let [author,setAuthor]=useState("")
    let [currentPage,setCurrentPage]=useState("")
    let [totalPage,setTotalPage]=useState("")
    
  return (
    <div>  
      <label htmlFor="title" >Enter Title</label>
      <input type="text" id="title" value={title} onChange={(e)=>{
        setTitle(e.target.value)
      }}/>

      <label htmlFor="author">Enter Author</label>
      <input type="text" id="author" value={author} onChange={(e)=>{
        setAuthor(e.target.value)
      }}/>

      <label htmlFor="currentPage">CurrentPage</label>
      <input type="text" id="currentPage" value={currentPage} onChange={(e)=>{
        setCurrentPage(e.target.value)
      }}/>
      <label htmlFor="totalPage">TotalPage</label>
      <input type="text" id="totalPage" value={totalPage} onChange={(e)=>{
        setTotalPage(e.target.value);
      }}/>

      <button onClick={ async (e)=>{
        let state=currentPage===totalPage?"Completed":"In Progress";
        let obj={
          "title":title,
          "author":author,
          "currentPage":currentPage,
          "totalPage":totalPage,
          "status":state,
          "username":user
        }
        if(obj.currentPage>obj.totalPage){
          alert("Current Page should be less than Total Page")
          return
        }
        let data= await api.post("/book",obj)
        setData((prev)=>{
          return [...prev,data.data]
        })
        setAdd(false)
      }}>Submit</button>
   </div>
  )
}

export default Button
