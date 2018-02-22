#include "coreir.h"
#include "coreir/passes/transform/split_inouts.h"

using namespace std;
using namespace CoreIR;

bool Passes::SplitInouts::runOnInstanceGraphNode(InstanceGraphNode& node) {
  Module* module = node.getModule();

  if (!module->hasDef()) {
    return false;
  }

  Context* c = module->getDef()->getContext();
  
  map<Select*, Select*> inoutsToOuts;
  map<Select*, Select*> inoutsToIns;
  for (auto field : module->getType()->getRecord()) {
    if (field.second->getDir() == Type::DK_InOut) {
      // TODO: Actually change the underlying array type instead
      // of just assuming its BitInOut
      string portName = field.first;
      string input = portName + "_input";
      string output = portName + "_output";

      node.appendField(input, c->Bit());
      node.appendField(output, c->BitIn());

      Wireable* self = module->getDef()->sel("self");

      Select* ioPort = self->sel(portName);
      Select* inputPort = self->sel(input);
      Select* outputPort = self->sel(output);

      cout << ioPort->toString() << endl;
      cout << inputPort->toString() << endl;
      cout << outputPort->toString() << endl;

      auto def = module->getDef();
      int width = 1;
      auto mux = def->addInstance(portName + "_split_mux",
                                  "coreir.mux",
                                  {{"width", Const::make(c, width)}});

      // Add array connections
      def->connect(mux->sel("in0")->sel(0), outputPort);
      // Connect mux->sel("in1") to inputPort

      // Get all connections
      vector<Select*> srcs = getSourceSelects(ioPort);
      assert(srcs.size() == 0);
      
      vector<Select*> receivers = getReceiverSelects(ioPort);
      assert(receivers.size() == 0);

      vector<Select*> ios = getIOSelects(ioPort);
      cout << "IO selects" << endl;
      for (auto io : ios) {
        cout << "\t" << io->toString() << endl;
      }

      set<Instance*> ioSources;
      for (auto io : ios) {
        Wireable* src = extractSource(io);
        assert(isa<Instance>(src));

        ioSources.insert(cast<Instance>(src));
      }

      assert(ioSources.size() == 2);

      Instance* tristateBuf = nullptr;
      Instance* tristateCast = nullptr;

      cout << "IO sources" << endl;
      for (auto ioSrc : ioSources) {
        cout << "\t" << ioSrc->toString() << endl;

        if (getQualifiedOpName(*ioSrc) == "coreir.triput") {
          tristateBuf = ioSrc;
        } else if (getQualifiedOpName(*ioSrc) == "coreir.triget") {
          tristateCast = ioSrc;
        }
      }

      
      assert(tristateBuf != nullptr);
      assert(tristateCast != nullptr);

      
      
    }
  }
  return false;
}
