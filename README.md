# Generative Code Modeling with Graphs

This is the code required to reproduce experiments in two of our papers on
modeling of programs, composed of three major components:
* A C# program required to extract (simplified) program graphs from C#
  source files, similar to our ICLR'18 paper
  [Learning to Represent Programs with Graphs](https://openreview.net/forum?id=BJOFETxR-).
  More precisely, it implements that paper apart from the speculative 
  dataflow component ("draw dataflow edges as if a variable would be used 
  in this place") and the alias analysis to filter equivalent variables.
* A TensorFlow model for program graphs, following ICLR'18 paper
  [Learning to Represent Programs with Graphs](https://openreview.net/forum?id=BJOFETxR-).
  This is a refactoring/partial rewrite of the original model, incorporating
  some new ideas on the representation of node labels from Cvitkovic et al.
  ([Open Vocabulary Learning on Source Code with a Graph-Structured Cache](https://arxiv.org/abs/1810.08305)).
* A TensorFlow model to generate new source code expressions conditional
  on their context, implementing our ICLR'19 paper
  [Generative Code Modeling with Graphs](https://openreview.net/forum?id=Bke4KsA5FX).

# Running the Code

The released code provides two components:
* Data Extraction: A C# project extracting graphs and expressions from a corpus
  of C# projects. The sources for this are in `DataExtraction/`.
* Modelling: A Python project learning model of expressions, conditionally on
  the program context. The sources for this are in `Models/`.

Note that the code is a research prototype; the documentation is generally
incomplete and code quality is varying.

## CSharp Data Extraction

### Building the data extractor
To build the data extraction, you need a .NET development environment (i.e.,
a working `dotnet` executable). Once this is set up, you can build the 
extractor as follows:
```
DataExtraction$ dotnet build
[...]
    ExpressionDataExtractor -> ExpressionDataExtractor\bin\Debug\net472\ExpressionDataExtractor.exe

Build succeeded.
[...]
```

### Using the data extractor
You can then use the resulting binary to extract contexts and expressions from
a C# project:
```
DataExtraction$ ExpressionDataExtractor/bin/Debug/net472/ExpressionDataExtractor.exe TestProject outputs/{graphs,types}
Writing graphs at outputs/graphs
Writing type hierarchies at outputs/types
[11/01/2019 14:07:05] Starting building all solutions in TestProject
[11/01/2019 14:07:05] Restoring packages for: TestProject/TinyTest.sln
[11/01/2019 14:07:05] In dir TestProject running nuget restore TinyTest.sln -NonInteractive -source https://api.nuget.org/v3/index.json
[11/01/2019 14:07:05] Nuget restore took 0 minutes.
[11/01/2019 14:07:06] Starting build of TestProject/TinyTest.sln
Compilations completed, completing extraction jobs...
Opening output file outputs/graphs/exprs-graph.0.jsonl.gz.
[11/01/2019 14:07:09] Extracted 15 expressions from TestProject/Program.cs.
```
Now, `outputs/graphs/exprs-graph.0.jsonl.gz` will contain (15) samples
consisting of a context graph and a target expression in tree form.
`ExpressionDataExtractor.exe --help` provides some information on
additional options.

*Note*: Building C# projects is often non-trivial (requiring [NuGet](https://www.nuget.org/)
and other libraries in the
path, preparing the build by running helper scripts, etc.). Roughly, data
extraction from a solution `Project.sln` will only succeed if running 
`MSBuild Project.sln` succeeds as well.

### Extractor Structure

Data extraction is split into two projects:
* `ExpressionDataExtractor`: This is the actual command-line utility with
  some code to find and build C# projects in a directory tree.
* `SourceGraphExtractionUtils`: This project contains the actual extraction
  logic. Almost all of the interesting logic is in `GraphDataExtractor`, which
  is in dire need of a refactoring. This class does four complex things:
  
    - Identify target expressions to extract (`SimpleExpressionIdentifier`).
    - Turn expressions into a simplified version of the C# syntax tree
      (`TurnIntoProductions`). This is needed because Roslyn does not expose an
      /abstract/ syntax tree, but a /full/ ST with all surface code artifacts.
    - Construction of a Program Graph as in "Learning to Represent Programs
      with Graphs", ICLR'18 (`ExtractSourceGraph`).
    - Extraction of a subgraph of limited size around a target expression,
      removing the target expression in the process (`CopySubgraphAroundHole`).
  
  There is some bare-bones documentation for these components, but if you
  are trying to understand them and are stuck, open an issue with concrete
  questions and better documentation will magically appear.

## Python Data Extraction

