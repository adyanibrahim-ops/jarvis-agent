from .agent import ask_jarvis
from .memory import (
    init_memory,
    save_memory,
    get_memories,
    delete_memory
)
from .tools import (
    calculate,
    get_system_info,
    list_files,
    read_file,
    find_files
)


init_memory()

print("=" * 50)
print("JARVIS ONLINE")
print("Type 'help' to see commands.")
print("=" * 50)


while True:

    user_message = input("\nYou: ").strip()

    if not user_message:
        continue

    command = user_message.lower()


    # EXIT
    if command == "exit":
        print("JARVIS: Shutting down.")
        break


    # HELP
    if command == "help":
        print("""
JARVIS commands:

remember <something>
memories
forget <id>

calculate <expression>

system info
list files
read file <path>
find file <filename>

exit
""")
        continue


    # MEMORY
    if command.startswith("remember "):

        memory = user_message[9:].strip()

        if memory:
            save_memory(memory)
            print("JARVIS: Memory saved.")
        else:
            print("JARVIS: Tell me what to remember.")

        continue


    if command == "memories":

        memories = get_memories()

        if not memories:
            print("JARVIS: No saved memories.")

        else:
            print("\nJARVIS MEMORY:\n")

            for memory_id, content, created_at in memories:
                print(f"[{memory_id}] {content}")

        continue


    if command.startswith("forget "):

        try:
            memory_id = int(user_message[7:].strip())
            delete_memory(memory_id)
            print("JARVIS: Memory deleted.")

        except ValueError:
            print("JARVIS: Please provide a valid memory ID.")

        continue


    # CALCULATOR
    if command.startswith("calculate "):

        expression = user_message[10:].strip()

        try:
            result = calculate(expression)
            print(f"JARVIS: {result}")

        except ValueError as e:
            print(f"JARVIS: {e}")

        continue


    # SYSTEM INFORMATION
    if command == "system info":

        try:
            info = get_system_info()

            print("\nJARVIS SYSTEM INFO:")

            for key, value in info.items():
                print(f"{key}: {value}")

        except Exception as e:
            print(f"JARVIS: {e}")

        continue


    # LIST FILES
    if command == "list files":

        try:
            files = list_files(".")

            print("\nJARVIS FILES:")

            for item in files:
                print(f"- {item}")

        except Exception as e:
            print(f"JARVIS: {e}")

        continue


    # READ FILE
    if command.startswith("read file "):

        file_path = user_message[10:].strip()

        try:
            content = read_file(file_path)

            print("\n" + content)

        except Exception as e:
            print(f"JARVIS: {e}")

        continue


    # FIND FILE
    if command.startswith("find file "):

        filename = user_message[10:].strip()

        try:
            results = find_files(".", filename)

            if results:
                print("\nJARVIS FOUND:")

                for result in results:
                    print(f"- {result}")

            else:
                print("JARVIS: No matching files found.")

        except Exception as e:
            print(f"JARVIS: {e}")

        continue


    # NORMAL AI REQUEST
    try:

        response = ask_jarvis(user_message)

        print(f"\nJARVIS: {response}")

    except Exception as e:

        print(f"\nERROR: {e}")