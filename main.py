from crewai import Agent, Task, Crew
from utils.pdf_parser import PDFParser
from gemini.gemini_api import GoogleGeminiAPI
from custom_LLM import GeminiLLM
import sys
from utils.pdf_creator import create_pdf

def main():
    try:
        for i in range(1, 10):
            print("\n")
        print("Welcome to the Blood Test Analysis System!")
        print("\nThis system will help you analyze a blood test report, find relevant health articles, and generate health recommendations based on the report and articles.")

        # Step 1: Parse PDF report
        pdf_file_path = input("\nEnter the path to the PDF blood test report: ")
        parser = PDFParser(pdf_file_path)
        text = parser.parse_text()
        
        if not text:
            print("Error: No text extracted from the PDF. Please check the PDF file.")
            return

        # Step 2: Initialize Google Gemini API and custom LLM
        gemini_api = GoogleGeminiAPI()
        custom_llm = GeminiLLM(gemini_api)

        # Step 3: Create agents
        analysis_agent = Agent(
            role="Blood Test Analyzer",
            goal="Analyze the blood test report and provide a summary that is understandable to a person without medical knowledge. Also make the summary short and simple ",
            backstory="A normal human is interpreting medical test results with no experience in clinical diagnostics.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        search_agent = Agent(
            role="Medical Article Researcher",
            goal="Find relevant health articles based on blood test analysis",
            backstory="A normal human with less knowledge of medical literature.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        recommendation_agent = Agent(
            role="Health Advisor",
            goal="Generate health recommendations based on blood test results and relevant articles",
            backstory="An experienced health advisor specializing in personalized recommendations, with a background in integrative medicine.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        # Step 4: Define tasks
        analyze_task = Task(
            description=f"Analyze the following blood test report and provide a summary that is understandable to a person without medical knowledge. Also make the summary short and simple  {text}",
            agent=analysis_agent,
            expected_output="A short summary of analysis of the blood test results, highlighting any abnormalities or areas of concern with short."
        )

        search_task = Task(
            description="Search for 5 relevant health articles based on the blood test analysis. Provide titles and URLs.",
            agent=search_agent,
            expected_output="A list of 5 relevant health articles with their titles and URLs, related to the findings in the blood test analysis."
        )

        recommend_task = Task(
            description="Generate health recommendations based on the blood test analysis and the found articles.",
            agent=recommendation_agent,
            expected_output="A set of actionable health recommendations based on the blood test analysis and information from the relevant articles."
        )

        # Step 5: Create and run the crew
        crew = Crew(
            agents=[analysis_agent, search_agent, recommendation_agent],
            tasks=[analyze_task, search_task, recommend_task],
            verbose=True
        )
        result = crew.kickoff()

        # Step 6: Display results
        print("\n--- Blood Test Analysis ---")
        print(f"\n{result.tasks_output[0].raw}")
        print("-" * 50)

        print("\n--- Relevant Articles ---")
        print(f"\n{result.tasks_output[1].raw}")
        print("-" * 50)

        print("\n--- Health Recommendations ---")
        print(f"\n{result.tasks_output[2].raw}")
        print("-" * 50)

        # Extract results
        analysis_output = next(output for output in result.tasks_output if "Analyze the following blood test report" in output.description)
        articles_output = next(output for output in result.tasks_output if "Search for 5 relevant health articles" in output.description)
        recommendations_output = next(output for output in result.tasks_output if "Generate health recommendations" in output.description)

        # Create PDF
        output_pdf_path = input("\nEnter the path to save the PDF report: ")
        create_pdf(analysis_output.raw, articles_output.raw, recommendations_output.raw, output_pdf_path)
        print(f"\nPDF report generated and saved to: {output_pdf_path}")


    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()