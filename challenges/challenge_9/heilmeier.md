# Heilmeier Questions

## What are you trying to do?

I am designing and building a simple hardware prototype of a spiking liquid state machine. My goal is to co-develop both the network structure and the hardware at the same time, so that they work together as efficiently as possible, rather than treating hardware as just a platform to run software.

## How is it done today, and what are the limits of current practice?
Today, liquid state machines are usually simulated in software, running on standard computer hardware. These simulations are flexible but slow, use a lot of energy, and don't fully capture what would happen if the system were built directly in hardware. Some hardware attempts have been made, but most simply copy the software structure without adjusting for real-world device constraints, which limits their speed, efficiency, and usefulness.

## What is new in your approach and why do you think it will be successful?

My approach is to co-design both the liquid state machine and the hardware at the same time, even at a small scale. By doing this, I can tune the network to match what the hardware can actually do well, and vice versa. This should result in a simpler, faster, and more energy-efficient prototype than if I just copied a software model. Because liquid state machines are known to be very flexible with structure and because small, simple spiking models are well-understood, I think this approach will work even within the limited time and resources of a class project.

## Who cares? If you are successful, what difference will it make?

If I succeed, it will show that even small-scale, brain-inspired networks can be efficiently mapped onto hardware if they are co-designed carefully. This could be a useful stepping stone for future research in efficient, neuromorphic computing, and could demonstrate how liquid state machines might be deployed in real-world low-power applications.

## What are the risks?

The main risk is that the hardware implementation might not work reliably within the limited time of a single academic term. Debugging hardware problems can be slow, and simulation might not fully predict real-world behavior. Another risk is that the final prototype may be too simple to convincingly demonstrate meaningful network behavior. I’m planning for these risks by starting simple and focusing on getting a minimal, functioning system first.

## How much will it cost?

Because this is a class project, I plan to keep costs low (hopefully zero). If necessary, I would consider spending a small amount on inexpensive, off-the-shelf components like microcontrollers, simple digital logic, or programmable boards.

## How long will it take?

Since this is a one-term project, hopefully one term.

**Mid-term Exam:** A working simulation showing that the network design is sound, and a partial hardware prototype that can spike and propagate signals.

**Final Exam:** A complete hardware prototype that can perform simple liquid state machine tasks (like classifying basic time-dependent inputs) and shows spiking activity similar to what was predicted in the simulation.
