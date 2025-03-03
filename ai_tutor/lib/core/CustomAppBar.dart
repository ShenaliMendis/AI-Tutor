import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  const CustomAppBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(top: 16, left: 16, right: 16),
      decoration: const BoxDecoration(
        color: Colors.white,
        // borderRadius: BorderRadius.vertical(bottom: Radius.circular(20)),
        // boxShadow: [
        //   BoxShadow(
        //     color: Colors.black12,
        //     blurRadius: 8,
        //     offset: Offset(0, 4),
        //   ),
        // ],
      ),
      child: SafeArea(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Title Section
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'AI Tutor',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'HexaElite',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
              ],
            ),
            // Action Section
            Row(
              children: [
                const Icon(Icons.location_on, color: Colors.blue, size: 18),
                const SizedBox(width: 4),
                const Text(
                  'Ashad, Samsudeen',
                  style: TextStyle(fontSize: 14, color: Colors.black),
                ),
                const Icon(Icons.arrow_drop_down, color: Colors.black),
                const SizedBox(width: 16),
                IconButton(
                  onPressed: () {
                    // Handle settings action
                  },
                  icon: const Icon(LucideIcons.settings, color: Colors.black),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(100); // Customize the height
}
