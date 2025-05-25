from src.script_parser import Script

if __name__ == "__main__":
    parser = Script()
    result = parser.parse("demo/data/Simulations/TestCity.txt")
    print("Parse result:", result)
    print("Parsed map types:", list(parser.m_mapTypes.keys()))
    print("Parsed unit types:", list(parser.m_unitTypes.keys()))
    print("Parsed agent types:", list(parser.m_agentTypes.keys()))
    print("Parsed resources:", list(parser.m_resources.keys()))
