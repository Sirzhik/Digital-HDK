from digital import CircuitManager, Position


if __name__ == "__main__":
    print("Digital HDK initialized successfully!")
    
    # print("\n=== Creating a new circuit ===")
    # mgr = CircuitManager()
    
    # input_element = mgr.elements.place(
    #     "Button",
    #     Position(x=300, y=400),
    #     {"Label": "A"}
    # )
    # print(f"Placed: {input_element}")

    # element1 = mgr.elements.place(
    #     "And",
    #     Position(x=520, y=380),
    #     {"Inputs": 3, "wideShape": True}
    # )
    # print(f"Placed: {element1}")
    
    # element2 = mgr.elements.place(
    #     "LED",
    #     Position(x=980, y=400),
    #     {"Label": "Q"}
    # )
    # print(f"Placed: {element2}")
    
    # print("\n=== Connecting elements ===")
    # wire = mgr.wires.connect(Position(x=600, y=400), Position(x=980, y=400))
    # print(f"Connected: {wire}")

    # mgr.wires.connect(Position(x=300, y=400), Position(x=520, y=380))
    # mgr.wires.connect(Position(x=300, y=400), Position(x=520, y=400))
    # mgr.wires.connect(Position(x=300, y=400), Position(x=520, y=420))
    
    # print(f"\nTotal elements: {len(mgr.elements.list_all())}")
    # print(f"Total wires: {len(mgr.wires.get_all_wires())}")
    
    # mgr.save("test_circuit.dig")
    # print("Circuit saved as test_circuit.dig")

    print("\n=== Loading JK.dig ===")
    try:
        jk_mgr = CircuitManager("test_circuit.dig")
        print(f"Loaded circuit: {jk_mgr.circuit}")
        print(f"Elements: {len(jk_mgr.elements.list_all())}")
        print(f"Wires: {len(jk_mgr.wires.get_all_wires())}")
        print(jk_mgr.elements.get(Position(x=280, y=540)))
        jk_mgr.elements.place("JK_FF", Position(x=200, y=540), {"Label": "JK"})
        jk_mgr.save("test_circuit.dig")
        print("Updated JK.dig with new JK Flip-Flop.")
        
        errors = jk_mgr.validate()
        if errors:
            print(f"Validation errors: {errors}")
        else:
            print("Validation passed!")
    
    except Exception as e:
        print(f"Error loading JK.dig: {e}")
    