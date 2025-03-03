from dotenv import load_dotenv
import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain.prompts import SystemMessagePromptTemplate
from langchain.agents import AgentExecutor

import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
#openai.api_key="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"
os.environ["OPENAI_API_KEY"] = openai.api_key
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
schema = """

create table dbo.Staff(
    StaffId int not null identity primary key,
    StaffFirstName varchar(20) not null
        constraint ck_Staff_firstName_cant_be_blank check(StaffFirstName <> ''),
    StaffLastName varchar(20) not null 
        constraint ck_Staff_lastName_cant_be_blank check(StaffLastName <> ''),
    UserName varchar(20) not null 
        constraint ck_Staff_UserName_cant_be_blank check(username <> '')
        constraint u_UserName unique,
)

create table dbo.Cuisine(
    CuisineId int not null identity primary key,
    CuisineType varchar(30) not null
        constraint u_cuisine_type unique
        constraint ck_CuisineType_cant_be_unique check(CuisineType <> '') 
)

create table dbo.Recipe(
    RecipeId int not null identity primary key, 
    CuisineId int not null constraint f_cuisine_recipe foreign key references cuisine(cuisineId),
    StaffId int not null constraint f_Staff_recipe foreign key references staff(staffId),
    RecipeName varchar(50) not null 
        constraint ck_recipe_name_cant_be_blank check(RecipeName <> '')
        constraint u_recipe_recipeName unique,
    Calories int not null 
            constraint ck_must_be_greater_than_zero check(calories > 0),
    DateDraft datetime not null default getdate()
        constraint ck_datedraft_cannot_be_future_date check(datedraft <= getdate()),
    DatePublished datetime null
        constraint ck_DatePublished_Cannot_be_future_date  check(datepublished <= getdate()),
    DateArchived datetime null
        constraint ck_DateArchived_cant_be_future_date check(datearchived <= getdate()),
    RecipeStatus as 
    case 
    when datepublished is null and datearchived is null then 'Draft'
    when datearchived is null then 'Published'
    when datearchived is not null then 'Archived'
    end,
        constraint ck_datepublished_must_be_greater_than_or_equal_to_datedraft check(datepublished >= DateDraft),
        constraint ck_datearchived_must_be_greater_than_or_equal_to_datedraft_and_datepublished check(datearchived >= DateDraft and datearchived >= datepublished),
    RecipePic as concat('recipe', '_', replace(recipename, ' ', '_'), '.jpeg'),      

)
go

create table dbo.MeasurementType(
    MeasurementTypeId int not null identity primary key,
    MeasurementType varchar(10) not null
        constraint ck_MeasurementTypeCant_be_blank check(measurementType <> '')
        constraint u_measurementType_must_be_unique unique(measurementType)
)
create table dbo.Ingredients(
    IngredientsId int not null identity primary key,
    IngredientName varchar(30) not null 
        constraint ck_ingredientName_cant_be_blank check(IngredientName <> '')
        constraint u_ingredientName unique,
    IngPic as concat('ingredient', '_', replace(IngredientName, ' ', '_'), '.jpeg')
)
go

create table dbo.RecipeIngredient(
    RecipeIngredientId int not null identity primary key,
    RecipeId int not null constraint f_recipe_recipeIngredient foreign key references recipe(recipeId),
    ingredientId int not null constraint f_ingredient_recipeIngredient foreign key references ingredients(ingredientsId),
    MeasurementTypeId int null constraint f_MeasurementType_MeasurementType foreign key references measurementType(MeasurementTypeId),
    IngredientAmt decimal(10,2) not null
        constraint ck_ingredientAmt_must_be_greater_than_zero check(ingredientamt > 0),
	IngredientSequence int not null 
        constraint ck_ingredientSequence_must_be_greater_than_zero check(IngredientSequence > 0)
       constraint u_ingredientSequence_recipe unique(IngredientSequence, recipeid)

)

create table dbo.Directions(
    DirectionsId int not null identity primary key,
    RecipeId int not null constraint f_recipe_directions foreign key references recipe(recipeId),
    Direction varchar(400)  not null
        constraint ck_direction_cant_be_blank check(direction<> ''),
   DirectionSequence int not null 
    constraint ck_dirSequence_must_be_greater_than_zero check(DirectionSequence >0)
    constraint u_directionSequence_recipeid unique(DirectionSequence, recipeid)
    ,
)



create table dbo.Meals(
    MealsId int not null identity primary key,
    StaffId int not null constraint f_staff_meals foreign key references staff(staffid),
    MealName varchar(30) 
        constraint u_mealName_meal unique
        constraint ck_MealName_cant_be_blank check(MealName <> ''),
    Active bit not null default (1),
    DateCreated date not null default getdate()
        constraint ck_datecreated_cannot_be_a_future_date check(datecreated<=getdate()),
    MealPic as concat('Meals', '_', replace(MealName, ' ', '_'), '.jpeg' )
    
)



create table dbo.Course(
    CourseId int not null identity primary key,
    CourseType varchar(30) not null
        constraint u_course_courseType unique
        constraint ck_courseType_cant_be_blank check(coursetype<> ''),
    CourseSequence int not null 
        constraint ck_sequence_needs_to_Be_greater_than_zero check(CourseSequence > 0)
        constraint u_courseSequence unique
)

create table dbo.CourseMeal(
    CourseMealId int not null identity primary key,
    CourseId int not null constraint f_Course_courseMeal foreign key references course(CourseId),
    MealsId int not null constraint f_meals_courseMeal foreign key references meals(MealsId),
        constraint u_meal_and_courseId_unique unique(MealsId, CourseId)
)

create table dbo.CourseRecipeCourseMeal(
    CourseRecipeId int not null identity primary key,
    courseMealId int not null constraint f_CourseMeal_CourseMeal foreign key references coursemeal(coursemealId),
    RecipeId int not null constraint f_Recipe_Courserecipe foreign key references recipe(recipeId),
    IsMain bit not null 
        constraint u_courseid_recipeid unique(coursemealid, recipeid),
)
create table dbo.Cookbook(
    CookbookId int not null identity primary key,
    StaffId int not null constraint f_staff_cookbook foreign key references staff(StaffId),
    CookbookName varchar(30) not null 
        constraint ck_cookbookName_cant_be_blank check(CookbookName <> '' )
        constraint u_cookbookName unique,
    Price decimal(5,2) not null
        constraint ck_price_must_be_greater_than_zero check(Price>0),
    Active bit not null default (1),
    DateCreated date not null  default getdate()
        constraint ck_CookbookdateCreated_cannot_be_a_future_Date check(datecreated<= getdate()),
    CookbookPic as concat('Cookbook', '_', replace(CookbookName, ' ', '_'), '.jpeg')--
)

create table dbo.CookbookRecipe(
    CookBookRecipeId int not null identity primary key,
    CookbookId int not null constraint f_cookbook_cookbookRecipe foreign key references cookbook(CookbookId),
	recipeId int not null constraint f_recipe_cookbookrecipe foreign key references recipe(recipeid),
    Seq int not null constraint ck_sequence_must_be_greater_than_zero check(Seq > 0),
    constraint u_recipeId_CookbookId unique(recipeid, CookbookId),
    constraint u_seq_cookbookid unique(seq, CookbookId)
)
"""
system_prompt = f"""
You are a helpful assistant that generates SQL queries based on the schema provided. 
Use this schema to generate valid SQL queries.

Schema:
{schema}

Now, please generate a SQL query based on the following user input:
"""
def generate_sql_query(user_input):
    prompt = system_prompt + f"\nUser Query: {user_input}\nSQL Query:"
    response = llm.predict(prompt)  # Use the language model to generate the SQL query
    return response.strip() 

    
user_query = st.text_area("Enter your related SQL-related query:", "List the most recently created recipe")
if st.button('Generate SQL Query'):
    try:
        # Generate the SQL query based on user input
        generated_sql = generate_sql_query(user_query)
        
        st.write("Generated SQL Query:")
        st.code(generated_sql, language="sql")
    except Exception as e:
        st.error(f"An error occurred: {e}")


        



# Simple request to check if API key is working
response = openai.completions.create(
    model="gpt-3.5-turbo",
    prompt="Hello, how are you?",
    max_tokens=5
)

print("API KEY STATUS:", response)


#check what models are available for api key
# import openai

# # Check available models
# models = openai.Model.list()
# for model in models['data']:
#     print(model['id'])
